from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.utils import timezone

from edc_appointment.constants import COMPLETE_APPT, IN_PROGRESS_APPT
from edc_appointment.creators import AppointmentsCreator
from edc_consent.consent_definition import ConsentDefinition
from edc_consent.exceptions import ConsentDefinitionError
from edc_consent.site_consents import site_consents
from edc_sites.site import sites as site_sites
from edc_sites.utils import valid_site_for_subject_or_raise
from edc_utils import convert_php_dateformat, formatted_datetime
from edc_utils.date import to_local

from .constants import OFF_SCHEDULE, ON_SCHEDULE
from .exceptions import (
    InvalidOffscheduleDate,
    NotOnScheduleError,
    NotOnScheduleForDateError,
    OnScheduleFirstAppointmentDateError,
    UnknownSubjectError,
)

if TYPE_CHECKING:
    from edc_appointment.models import Appointment
    from edc_model.models import BaseUuidModel
    from edc_registration.models import RegisteredSubject
    from edc_sites.model_mixins import SiteModelMixin
    from edc_visit_tracking.model_mixins import VisitModelMixin as Base

    from .model_mixins import OnScheduleModelMixin
    from .models import OffSchedule, OnSchedule, SubjectScheduleHistory
    from .schedule import Schedule
    from .visit_schedule import VisitSchedule

    class RelatedVisitModel(SiteModelMixin, Base, BaseUuidModel):
        pass

    class OnScheduleLikeModel(OnScheduleModelMixin): ...


class SubjectSchedule:
    """A class that puts a subject on to a schedule or takes a subject
    off of a schedule.

    This class is instantiated by the Schedule class.
    """

    history_model = "edc_visit_schedule.subjectschedulehistory"
    registered_subject_model = "edc_registration.registeredsubject"
    appointments_creator_cls = AppointmentsCreator

    def __init__(
        self,
        subject_identifier: str,
        visit_schedule: VisitSchedule = None,
        schedule: Schedule = None,
    ):
        self.subject_identifier: str = subject_identifier
        self.visit_schedule: VisitSchedule = visit_schedule
        self.schedule: Schedule = schedule
        self.schedule_name: str = schedule.name
        self.visit_schedule_name: str = self.visit_schedule.name
        self.onschedule_model: str = schedule.onschedule_model
        self.offschedule_model: str = schedule.offschedule_model
        self.appointment_model: str = schedule.appointment_model

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(subject_identifier={self.subject_identifier},"
            f"visit_schedule={self.visit_schedule},schedule={self.schedule})"
        )

    def __str__(self):
        return f"{self.subject_identifier} {self.visit_schedule_name}.{self.schedule_name}"

    @property
    def onschedule_model_cls(self) -> type[OnSchedule]:
        return django_apps.get_model(self.onschedule_model)

    @property
    def offschedule_model_cls(self) -> type[OffSchedule]:
        return django_apps.get_model(self.offschedule_model)

    @property
    def history_model_cls(self) -> type[SubjectScheduleHistory]:
        return django_apps.get_model(self.history_model)

    @property
    def appointment_model_cls(self) -> type[Appointment]:
        return django_apps.get_model(self.appointment_model)

    def put_on_schedule(
        self,
        onschedule_datetime: datetime | None,
        first_appt_datetime: datetime | None = None,
        skip_baseline: bool | None = None,
        skip_get_current_site: bool | None = None,
        consent_definition: ConsentDefinition | None = None,
    ):
        """Puts a subject on-schedule.

        A person is put on schedule by creating an instance
        of the onschedule_model, if it does not already exist,
        and updating the history_obj.

        Appointment are created here by calling the
        appointments_creator_cls.
        """
        onschedule_datetime = onschedule_datetime or timezone.now()
        if not consent_definition and len(self.schedule.consent_definitions) == 1:
            consent_definition = self.schedule.consent_definitions[0]
        elif not consent_definition:
            raise ConsentDefinitionError(
                "Unable to put on schedule. Consent definition may not be none. "
                f"Expected one of {self.schedule.consent_definitions}"
            )
        elif consent_definition not in self.schedule.consent_definitions:
            raise ConsentDefinitionError(
                "Unable to put on schedule. Invalid consent definition for schedule. "
                f"Got schedule={self.schedule}, cdef={consent_definition}. "
                f"Expected one of {self.schedule.consent_definitions}"
            )

        site = valid_site_for_subject_or_raise(
            self.subject_identifier, skip_get_current_site=skip_get_current_site
        )
        single_site = site_sites.get(site.id)
        site_consents.filter_cdefs_by_site_or_raise(
            site=single_site,
            consent_definitions=[consent_definition],
        )
        if not self.onschedule_model_cls.objects.filter(
            subject_identifier=self.subject_identifier
        ).exists():
            # this is how you get on a schedule. Only!
            self.onschedule_model_cls.objects.create(
                subject_identifier=self.subject_identifier,
                onschedule_datetime=onschedule_datetime,
                site=site,
            )
        try:
            history_obj = self.history_model_cls.objects.get(
                subject_identifier=self.subject_identifier,
                schedule_name=self.schedule_name,
                visit_schedule_name=self.visit_schedule_name,
            )
        except ObjectDoesNotExist:
            history_obj = self.history_model_cls.objects.create(
                subject_identifier=self.subject_identifier,
                onschedule_model=self.onschedule_model,
                offschedule_model=self.offschedule_model,
                schedule_name=self.schedule_name,
                visit_schedule_name=self.visit_schedule_name,
                onschedule_datetime=onschedule_datetime,
                schedule_status=ON_SCHEDULE,
                site=site,
            )
        if history_obj.schedule_status == ON_SCHEDULE:
            # create appointments per schedule
            creator = self.appointments_creator_cls(
                report_datetime=onschedule_datetime,
                subject_identifier=self.subject_identifier,
                schedule=self.schedule,
                visit_schedule=self.visit_schedule,
                appointment_model=self.appointment_model,
                site_id=site.id,
                skip_baseline=skip_baseline,
            )
            if first_appt_datetime and first_appt_datetime < onschedule_datetime:
                raise OnScheduleFirstAppointmentDateError(
                    "First appt datetime cannot be before onschedule datetime. "
                    f"Got {first_appt_datetime} < {onschedule_datetime}"
                )
            creator.create_appointments(
                first_appt_datetime or onschedule_datetime,
                skip_get_current_site=skip_get_current_site,
            )

    def refresh_appointments(self):
        creator = self.appointments_creator_cls(
            report_datetime=self.onschedule_obj.onschedule_datetime,
            subject_identifier=self.subject_identifier,
            schedule=self.schedule,
            visit_schedule=self.visit_schedule,
            appointment_model=self.appointment_model,
            site_id=self.registered_or_raise().site.id,
            skip_baseline=True,
        )
        creator.create_appointments(self.onschedule_obj.onschedule_datetime)

        try:
            offschedule_obj = self.offschedule_model_cls.objects.get(
                subject_identifier=self.subject_identifier
            )
        except ObjectDoesNotExist:
            pass
        else:
            # clear future appointments
            self.appointment_model_cls.objects.delete_for_subject_after_date(
                subject_identifier=self.subject_identifier,
                cutoff_datetime=offschedule_obj.offschedule_datetime,
                visit_schedule_name=self.visit_schedule_name,
                schedule_name=self.schedule_name,
            )

    def take_off_schedule(self, offschedule_datetime: datetime):
        """Takes a subject off-schedule.

        A person is taken off-schedule by:
        * creating an instance of the offschedule_model,
          if it does not already exist,
        * updating the history_obj
        * deleting future appointments
        """
        # create offschedule_model_obj if it does not exist
        rs_obj = self.registered_or_raise()
        if not self.offschedule_model_cls.objects.filter(
            subject_identifier=self.subject_identifier
        ).exists():
            self.offschedule_model_cls.objects.create(
                subject_identifier=self.subject_identifier,
                offschedule_datetime=offschedule_datetime,
                site=rs_obj.site,
            )

        # get existing history obj or raise
        try:
            history_obj = self.history_model_cls.objects.get(
                subject_identifier=self.subject_identifier,
                schedule_name=self.schedule_name,
                visit_schedule_name=self.visit_schedule_name,
            )
        except ObjectDoesNotExist:
            raise NotOnScheduleError(
                "Failed to take subject off schedule. "
                f"Subject has not been put on schedule "
                f"'{self.visit_schedule_name}.{self.schedule_name}'. "
                f"Got '{self.subject_identifier}'."
            )

        if history_obj:
            self.update_history_or_raise(
                history_obj=history_obj,
                offschedule_datetime=offschedule_datetime,
            )

            self._update_in_progress_appointment()

            # clear future appointments
            self.appointment_model_cls.objects.delete_for_subject_after_date(
                subject_identifier=self.subject_identifier,
                cutoff_datetime=offschedule_datetime,
                visit_schedule_name=self.visit_schedule_name,
                schedule_name=self.schedule_name,
            )

    def update_history_or_raise(
        self,
        history_obj=None,
        offschedule_datetime=None,
        update=None,
    ):
        """Updates the history model instance.

        Raises an error if the offschedule_datetime is before the
        onschedule_datetime or before the last visit.
        """
        update = True if update is None else update
        if not self.history_model_cls.objects.filter(
            subject_identifier=self.subject_identifier,
            schedule_name=self.schedule_name,
            visit_schedule_name=self.visit_schedule_name,
            onschedule_datetime__lte=offschedule_datetime,
        ).exists():
            raise InvalidOffscheduleDate(
                "Failed to take subject off schedule. "
                "Offschedule date cannot precede onschedule date. "
                f"Subject was put on schedule {self.visit_schedule_name}."
                f"{self.schedule_name} on {history_obj.onschedule_datetime}. "
                f"Got {offschedule_datetime}."
            )
        # confirm date not before last visit
        related_visit_model_attr = self.appointment_model_cls.related_visit_model_attr()
        try:
            appointments = self.appointment_model_cls.objects.get(
                subject_identifier=self.subject_identifier,
                schedule_name=self.schedule_name,
                visit_schedule_name=self.visit_schedule_name,
                **{f"{related_visit_model_attr}__report_datetime__gt": (offschedule_datetime)},
            )
        except ObjectDoesNotExist:
            appointments = None
        except MultipleObjectsReturned:
            appointments = self.appointment_model_cls.objects.filter(
                subject_identifier=self.subject_identifier,
                schedule_name=self.schedule_name,
                visit_schedule_name=self.visit_schedule_name,
                **{f"{related_visit_model_attr}__report_datetime__gt": (offschedule_datetime)},
            )
        if appointments:
            raise InvalidOffscheduleDate(
                f"Failed to take subject off schedule. "
                f"Visits exist after proposed offschedule date. "
                f"Got '{formatted_datetime(offschedule_datetime)}'."
            )
        if update:
            # update history object
            history_obj.offschedule_datetime = offschedule_datetime
            history_obj.schedule_status = OFF_SCHEDULE
            history_obj.save()

    def _update_in_progress_appointment(self):
        """Updates the "in_progress" appointment and clears
        future appointments.
        """
        for obj in self.appointment_model_cls.objects.filter(
            subject_identifier=self.subject_identifier,
            schedule_name=self.schedule_name,
            visit_schedule_name=self.visit_schedule_name,
            appt_status=IN_PROGRESS_APPT,
        ):
            obj.appt_status = COMPLETE_APPT
            obj.save()

    def registered_or_raise(self) -> RegisteredSubject:
        """Return an instance RegisteredSubject or raise an exception
        if instance does not exist.
        """
        model_cls = django_apps.get_model(self.registered_subject_model)
        try:
            obj = model_cls.objects.get(subject_identifier=self.subject_identifier)
        except ObjectDoesNotExist:
            raise UnknownSubjectError(
                f"Failed to put subject on schedule. Unknown subject. "
                f"Searched `{self.registered_subject_model}`. "
                f"Got subject_identifier=`{self.subject_identifier}`."
            )
        return obj

    @property
    def onschedule_obj(self) -> OnScheduleLikeModel:
        try:
            onschedule_obj = self.onschedule_model_cls.objects.get(
                subject_identifier=self.subject_identifier
            )
        except ObjectDoesNotExist:
            raise NotOnScheduleError(
                f"Subject has not been put on a schedule `{self.schedule_name}`. "
                f"Got subject_identifier=`{self.subject_identifier}`."
            )
        return onschedule_obj

    def onschedule_or_raise(self, report_datetime=None, compare_as_datetimes=None):
        """Raise an exception if subject is not on the schedule during
        the given date.
        """
        compare_as_datetimes = True if compare_as_datetimes is None else compare_as_datetimes

        onschedule_obj = self.onschedule_obj

        try:
            offschedule_datetime = self.offschedule_model_cls.objects.values_list(
                "offschedule_datetime", flat=True
            ).get(subject_identifier=self.subject_identifier)
        except ObjectDoesNotExist:
            offschedule_datetime = None

        if compare_as_datetimes:
            in_date_range = (
                onschedule_obj.onschedule_datetime
                <= report_datetime
                <= (offschedule_datetime or timezone.now())
            )
        else:
            in_date_range = (
                onschedule_obj.onschedule_datetime.date()
                <= report_datetime.date()
                <= (offschedule_datetime or timezone.now()).date()
            )

        if offschedule_datetime and not in_date_range:
            formatted_offschedule_datetime = to_local(offschedule_datetime).strftime(
                convert_php_dateformat(settings.SHORT_DATETIME_FORMAT)
            )
            formatted_report_datetime = to_local(report_datetime).strftime(
                convert_php_dateformat(settings.SHORT_DATETIME_FORMAT)
            )
            raise NotOnScheduleForDateError(
                f"Subject not on schedule '{self.schedule_name}' for "
                f"report date '{formatted_report_datetime}'. "
                f"Got '{self.subject_identifier}' was taken "
                f"off this schedule on '{formatted_offschedule_datetime}'."
            )
