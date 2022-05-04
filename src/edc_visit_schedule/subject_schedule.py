from datetime import datetime
from typing import Optional

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from edc_appointment.constants import COMPLETE_APPT, IN_PROGRESS_APPT
from edc_appointment.creators import AppointmentsCreator
from edc_consent import NotConsentedError
from edc_utils import convert_php_dateformat, formatted_datetime, get_utcnow

from .constants import OFF_SCHEDULE, ON_SCHEDULE
from .exceptions import (
    InvalidOffscheduleDate,
    NotOnScheduleError,
    NotOnScheduleForDateError,
    OnScheduleFirstAppointmentDateError,
    SubjectScheduleError,
    UnknownSubjectError,
)


class SubjectSchedule:
    """A class that puts a subject on to a schedule or takes a subject
    off of a schedule.

    This class is instantiated by the Schedule class.
    """

    history_model = "edc_visit_schedule.subjectschedulehistory"
    registered_subject_model = "edc_registration.registeredsubject"
    appointments_creator_cls = AppointmentsCreator

    def __init__(self, visit_schedule=None, schedule=None):
        self.visit_schedule = visit_schedule
        self.schedule = schedule
        self.schedule_name = schedule.name
        self.visit_schedule_name = self.visit_schedule.name
        self.onschedule_model = schedule.onschedule_model
        self.consent_model = schedule.consent_model
        self.offschedule_model = schedule.offschedule_model
        self.appointment_model = schedule.appointment_model

    @property
    def onschedule_model_cls(self):
        return django_apps.get_model(self.onschedule_model)

    @property
    def offschedule_model_cls(self):
        return django_apps.get_model(self.offschedule_model)

    @property
    def history_model_cls(self):
        return django_apps.get_model(self.history_model)

    @property
    def appointment_model_cls(self):
        return django_apps.get_model(self.appointment_model)

    @property
    def visit_model_cls(self):
        return self.appointment_model_cls.visit_model_cls()

    @property
    def consent_model_cls(self):
        return django_apps.get_model(self.consent_model)

    def put_on_schedule(
        self,
        subject_identifier: Optional[str] = None,
        onschedule_datetime: Optional[datetime] = None,
        first_appt_datetime: Optional[datetime] = None,
        skip_baseline: Optional[bool] = None,
    ):
        """Puts a subject on-schedule.

        A person is put on schedule by creating an instance
        of the onschedule_model, if it does not already exist,
        and updating the history_obj.
        """
        onschedule_datetime = onschedule_datetime or get_utcnow()
        if not self.onschedule_model_cls.objects.filter(
            subject_identifier=subject_identifier
        ).exists():
            self.registered_or_raise(subject_identifier=subject_identifier)
            self.consented_or_raise(subject_identifier=subject_identifier)
            self.onschedule_model_cls.objects.create(
                subject_identifier=subject_identifier,
                onschedule_datetime=onschedule_datetime,
            )
        try:
            history_obj = self.history_model_cls.objects.get(
                subject_identifier=subject_identifier,
                schedule_name=self.schedule_name,
                visit_schedule_name=self.visit_schedule_name,
            )
        except ObjectDoesNotExist:
            history_obj = self.history_model_cls.objects.create(
                subject_identifier=subject_identifier,
                onschedule_model=self.onschedule_model,
                offschedule_model=self.offschedule_model,
                schedule_name=self.schedule_name,
                visit_schedule_name=self.visit_schedule_name,
                onschedule_datetime=onschedule_datetime,
                schedule_status=ON_SCHEDULE,
            )
        if history_obj.schedule_status == ON_SCHEDULE:
            # create appointments per schedule
            creator = self.appointments_creator_cls(
                report_datetime=onschedule_datetime,
                subject_identifier=subject_identifier,
                schedule=self.schedule,
                visit_schedule=self.visit_schedule,
                appointment_model=self.appointment_model,
                skip_baseline=skip_baseline,
            )
            if first_appt_datetime and first_appt_datetime < onschedule_datetime:
                raise OnScheduleFirstAppointmentDateError(
                    "First appt datetime cannot be before onschedule datetime. "
                    f"Got {first_appt_datetime} < {onschedule_datetime}"
                )
            creator.create_appointments(first_appt_datetime or onschedule_datetime)

    def take_off_schedule(self, subject_identifier=None, offschedule_datetime=None):
        """Takes a subject off-schedule.

        A person is taken off-schedule by:
        * creating an instance of the offschedule_model,
          if it does not already exist,
        * updating the history_obj
        * deleting future appointments
        """
        # create offschedule_model_obj if it does not exist
        if not self.offschedule_model_cls.objects.filter(
            subject_identifier=subject_identifier
        ).exists():
            self.offschedule_model_cls.objects.create(
                subject_identifier=subject_identifier,
                offschedule_datetime=offschedule_datetime,
            )

        # get existing history obj or raise
        try:
            history_obj = self.history_model_cls.objects.get(
                subject_identifier=subject_identifier,
                schedule_name=self.schedule_name,
                visit_schedule_name=self.visit_schedule_name,
            )
        except ObjectDoesNotExist:
            raise NotOnScheduleError(
                "Failed to take subject off schedule. "
                f"Subject has not been put on schedule "
                f"'{self.visit_schedule_name}.{self.schedule_name}'. "
                f"Got '{subject_identifier}'."
            )

        if history_obj:
            self.update_history_or_raise(
                history_obj=history_obj,
                subject_identifier=subject_identifier,
                offschedule_datetime=offschedule_datetime,
            )

            self._update_in_progress_appointment(subject_identifier=subject_identifier)

            # clear future appointments
            self.appointment_model_cls.objects.delete_for_subject_after_date(
                subject_identifier=subject_identifier,
                cutoff_datetime=offschedule_datetime,
                visit_schedule_name=self.visit_schedule_name,
                schedule_name=self.schedule_name,
            )

    def update_history_or_raise(
        self,
        history_obj=None,
        subject_identifier=None,
        offschedule_datetime=None,
        update=None,
    ):
        """Updates the history model instance.

        Raises an error if the offschedule_datetime is before the
        onschedule_datetime or before the last visit.
        """
        update = True if update is None else update
        if not self.history_model_cls.objects.filter(
            subject_identifier=subject_identifier,
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
                subject_identifier=subject_identifier,
                schedule_name=self.schedule_name,
                visit_schedule_name=self.visit_schedule_name,
                **{f"{related_visit_model_attr}__report_datetime__gt": offschedule_datetime},
            )
        except ObjectDoesNotExist:
            appointments = None
        except MultipleObjectsReturned:
            appointments = self.appointment_model_cls.objects.filter(
                subject_identifier=subject_identifier,
                schedule_name=self.schedule_name,
                visit_schedule_name=self.visit_schedule_name,
                **{f"{related_visit_model_attr}__report_datetime__gt": offschedule_datetime},
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

    def _update_in_progress_appointment(self, subject_identifier=None):
        """Updates the "in_progress" appointment and clears
        future appointments.
        """
        for obj in self.appointment_model_cls.objects.filter(
            subject_identifier=subject_identifier,
            schedule_name=self.schedule_name,
            visit_schedule_name=self.visit_schedule_name,
            appt_status=IN_PROGRESS_APPT,
        ):
            obj.appt_status = COMPLETE_APPT
            obj.save()

    def resave(self, subject_identifier=None):
        """Resaves the onschedule model instance to trigger, for example,
        appointment creation (if using edc_appointment mixin).
        """
        obj = self.onschedule_model_cls.objects.get(subject_identifier=subject_identifier)
        obj.save()

    def registered_or_raise(self, subject_identifier=None):
        """Raises an exception if RegisteredSubject instance does not exist."""
        model_cls = django_apps.get_model(self.registered_subject_model)
        try:
            model_cls.objects.get(subject_identifier=subject_identifier)
        except ObjectDoesNotExist:
            raise UnknownSubjectError(
                f"Failed to put subject on schedule. Unknown subject. "
                f"Searched `{self.registered_subject_model}`. "
                f"Got subject_identifier=`{subject_identifier}`."
            )

    def consented_or_raise(self, subject_identifier=None):
        """Raises an exception if one or more consents do not exist."""
        if not self.consent_model_cls.objects.filter(
            subject_identifier=subject_identifier
        ).exists():
            raise NotConsentedError(
                f"Failed to put subject on schedule. Consent not found. "
                f"Using consent model '{self.consent_model}' "
                f"subject identifier={subject_identifier}."
            )

    def onschedule_or_raise(
        self, subject_identifier=None, report_datetime=None, compare_as_datetimes=None
    ):
        """Raise an exception if subject is not on the schedule during
        the given date.
        """
        compare_as_datetimes = True if compare_as_datetimes is None else compare_as_datetimes
        try:
            onschedule_obj = self.onschedule_model_cls.objects.get(
                subject_identifier=subject_identifier
            )
        except ObjectDoesNotExist:
            raise NotOnScheduleError(
                f"Subject has not been put on a schedule `{self.schedule_name}`. "
                f"Got subject_identifier=`{subject_identifier}`."
            )

        try:
            offschedule_datetime = self.offschedule_model_cls.objects.values_list(
                "offschedule_datetime", flat=True
            ).get(subject_identifier=subject_identifier)
        except ObjectDoesNotExist:
            offschedule_datetime = None

        if compare_as_datetimes:
            in_date_range = (
                onschedule_obj.onschedule_datetime
                <= report_datetime
                <= (offschedule_datetime or get_utcnow())
            )
        else:
            in_date_range = (
                onschedule_obj.onschedule_datetime.date()
                <= report_datetime.date()
                <= (offschedule_datetime or get_utcnow()).date()
            )

        if offschedule_datetime and not in_date_range:
            formatted_offschedule_datetime = offschedule_datetime.strftime(
                convert_php_dateformat(settings.SHORT_DATE_FORMAT)
            )
            formatted_report_datetime = report_datetime.strftime(
                convert_php_dateformat(settings.SHORT_DATE_FORMAT)
            )
            raise NotOnScheduleForDateError(
                f"Subject not on schedule '{self.schedule_name}' for "
                f"report date '{formatted_report_datetime}'. "
                f"Got '{subject_identifier}' was taken "
                f"off this schedule on '{formatted_offschedule_datetime}'."
            )
        return None

    def check(self):
        try:
            self.onschedule_model_cls
            self.offschedule_model_cls
            self.appointment_model_cls
        except LookupError as e:
            raise SubjectScheduleError(e)
