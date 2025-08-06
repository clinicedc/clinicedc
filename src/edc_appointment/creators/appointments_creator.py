from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from django.apps import apps as django_apps
from django.db.models.deletion import ProtectedError
from edc_facility.exceptions import FacilityError
from edc_facility.utils import get_facility

from ..exceptions import CreateAppointmentError
from .appointment_creator import AppointmentCreator

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from edc_visit_schedule.schedule import Schedule
    from edc_visit_schedule.visit_schedule import VisitSchedule

    from ..models import Appointment


class AppointmentsCreator:
    """Note: Appointments are created using this class by
    the visit schedule.

    See also: edc_visit_schedule SubjectSchedule

    """

    appointment_creator_cls = AppointmentCreator

    def __init__(
        self,
        subject_identifier: str | None = None,
        visit_schedule: VisitSchedule | None = None,
        schedule: Schedule | None = None,
        report_datetime: datetime | None = None,
        appointment_model: str = None,
        site_id: int | None = None,
        skip_baseline: bool | None = None,
    ):
        self.subject_identifier: str = subject_identifier
        self.visit_schedule: VisitSchedule = visit_schedule
        self.schedule: Schedule = schedule
        self.report_datetime: datetime = report_datetime
        self.appointment_model: str = appointment_model
        self.site_id = site_id
        self.skip_baseline: bool | None = skip_baseline

    @property
    def appointment_model_cls(self) -> Appointment:
        return django_apps.get_model(self.appointment_model)

    def create_appointments(
        self,
        base_appt_datetime=None,
        taken_datetimes=None,
        skip_get_current_site: bool | None = None,
    ) -> QuerySet[Appointment]:
        """Creates appointments when called by post_save signal.

        Timepoint datetimes are adjusted according to the available
        days in the facility.
        """
        taken_datetimes = taken_datetimes or []
        base_appt_datetime = (base_appt_datetime or self.report_datetime).astimezone(
            ZoneInfo("UTC")
        )

        timepoint_dates = self.schedule.visits_for_subject(
            subject_identifier=self.subject_identifier,
            report_datetime=base_appt_datetime,
            site_id=self.site_id,
        ).timepoint_dates(dt=base_appt_datetime)

        for visit, timepoint_datetime in timepoint_dates.items():
            try:
                facility = get_facility(visit.facility_name)
            except FacilityError as e:
                raise CreateAppointmentError(
                    f"{e} See {repr(visit)}. Got facility_name={visit.facility_name}"
                )
            appointment = self.update_or_create_appointment(
                visit=visit,
                taken_datetimes=taken_datetimes,
                timepoint_datetime=timepoint_datetime,
                facility=facility,
                skip_get_current_site=skip_get_current_site,
            )
            taken_datetimes.append(appointment.appt_datetime)

        # check for existing appointment model instances after last timepoint
        try:
            last_timepoint = list(timepoint_dates.keys())[-1].timepoint
        except IndexError:
            pass
        else:
            self.delete_appointments_after_timepoint(last_timepoint)

        appointments = self.appointment_model_cls.objects.filter(
            subject_identifier=self.subject_identifier,
            site_id=self.site_id,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
        ).order_by("timepoint")
        return appointments

    def update_or_create_appointment(self, **kwargs) -> Appointment:
        """Updates or creates an appointment for this subject
        for the visit.
        """
        opts = dict(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            appointment_model=self.appointment_model,
            skip_baseline=self.skip_baseline,
            **kwargs,
        )
        appointment_creator = self.appointment_creator_cls(**opts)
        return appointment_creator.appointment

    def delete_unused_appointments(self) -> None:
        appointments = self.appointment_model.objects.filter(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
        )
        for appointment in appointments:
            try:
                appointment.delete()
            except ProtectedError:
                pass

    def delete_appointments_after_timepoint(self, last_timepoint) -> None:
        """Delete appointments after a given timepoint.

        This is only relavent if the consent definition is extended
        by a consent definition extension.
        """
        for appointment in self.appointment_model_cls.objects.filter(
            subject_identifier=self.subject_identifier,
            site_id=self.site_id,
            timepoint__gt=last_timepoint,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
        ):
            try:
                appointment.delete()
            except ProtectedError:
                pass
