from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from django.db.models.deletion import ProtectedError
from edc_facility.exceptions import FacilityError
from edc_facility.utils import get_facility

from .appointment_creator import AppointmentCreator, CreateAppointmentError

if TYPE_CHECKING:
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
        appointment_model: Appointment = None,
        skip_baseline: bool | None = None,
    ):
        self.subject_identifier = subject_identifier
        self.visit_schedule = visit_schedule
        self.schedule = schedule
        self.report_datetime = report_datetime
        self.appointment_model = appointment_model
        self.skip_baseline = skip_baseline

    def create_appointments(
        self, base_appt_datetime=None, taken_datetimes=None
    ) -> list[Appointment]:
        """Creates appointments when called by post_save signal.

        Timepoint datetimes are adjusted according to the available
        days in the facility.
        """
        appointments = []
        taken_datetimes = taken_datetimes or []
        base_appt_datetime = (base_appt_datetime or self.report_datetime).astimezone(
            ZoneInfo("UTC")
        )
        timepoint_dates = self.schedule.visits.timepoint_dates(dt=base_appt_datetime)
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
            )
            appointments.append(appointment)
            taken_datetimes.append(appointment.appt_datetime)
        return appointments

    def update_or_create_appointment(self, **kwargs) -> Appointment:
        """Updates or creates an appointment for this subject
        for the visit.
        """
        appointment_creator = self.appointment_creator_cls(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            appointment_model=self.appointment_model,
            skip_baseline=self.skip_baseline,
            **kwargs,
        )
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
