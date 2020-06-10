from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.utils import IntegrityError
from django.utils.timezone import is_naive
from edc_facility.facility import FacilityError

from ..constants import CLINIC, SCHEDULED_APPT


class CreateAppointmentError(Exception):
    pass


class CreateAppointmentDateError(Exception):
    pass


class AppointmentCreatorError(Exception):
    pass


class AppointmentCreator:
    def __init__(
        self,
        timepoint_datetime=None,
        timepoint=None,
        visit=None,
        visit_code_sequence=None,
        facility=None,
        appointment_model=None,
        taken_datetimes=None,
        subject_identifier=None,
        visit_schedule_name=None,
        schedule_name=None,
        default_appt_type=None,
        default_appt_reason=None,
        appt_status=None,
        appt_reason=None,
        suggested_datetime=None,
    ):
        self._appointment = None
        self._appointment_model_cls = None
        self._default_appt_type = default_appt_type
        self._default_appt_reason = default_appt_reason
        self.subject_identifier = subject_identifier
        self.visit_schedule_name = visit_schedule_name
        self.schedule_name = schedule_name
        self.appt_status = appt_status
        self.appt_reason = appt_reason
        self.appointment_model = appointment_model
        # already taken appt_datetimes for this subject
        self.taken_datetimes = taken_datetimes or []
        self.visit = visit
        self.visit_code_sequence = visit_code_sequence or 0
        self.timepoint = timepoint
        try:
            if is_naive(timepoint_datetime):
                raise ValueError(
                    f"Naive datetime not allowed. {repr(self)}. "
                    f"Got {timepoint_datetime}"
                )
            else:
                self.timepoint_datetime = timepoint_datetime
        except AttributeError:
            raise AppointmentCreatorError(
                f"Expected 'timepoint_datetime'. Got None. {repr(self)}."
            )
        # suggested_datetime (defaults to timepoint_datetime)
        # If provided, the rules for window period/rdelta relative
        # to timepoint_datetime still apply.
        if suggested_datetime and is_naive(suggested_datetime):
            raise ValueError(
                f"Naive datetime not allowed. {repr(self)}. "
                f"Got {suggested_datetime}"
            )
        else:
            self.suggested_datetime = suggested_datetime or self.timepoint_datetime
        self.facility = facility or visit.facility
        if not self.facility:
            raise AppointmentCreatorError(
                f"facility_name not defined. See {repr(visit)}"
            )
        self.appointment

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(subject_identifier={self.subject_identifier}, "
            f"visit_code={self.visit.code}.{self.visit_code_sequence}@{self.timepoint})"
        )

    def __str__(self):
        return self.subject_identifier

    @property
    def appointment(self):
        """Returns a newly created or updated appointment model instance.
        """
        if not self._appointment:
            try:
                self._appointment = self.appointment_model_cls.objects.get(
                    **self.options
                )
            except ObjectDoesNotExist:
                self._appointment = self._create()
            else:
                self._appointment = self._update(appointment=self._appointment)
        return self._appointment

    @property
    def available_rdate(self, dt=None):
        available_datetime = self.facility.available_rdate(dt)
        return available_datetime

    @property
    def options(self):
        """Returns default options to "get" an existing
        appointment model instance.
        """
        options = dict(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule_name,
            schedule_name=self.schedule_name,
            visit_code=self.visit.code,
            visit_code_sequence=self.visit_code_sequence,
            timepoint=self.timepoint or self.visit.timepoint,
        )
        if self.appt_status:
            options.update(appt_status=self.appt_status)
        return options

    def _create(self):
        """Returns a newly created appointment model instance.
        """
        try:
            with transaction.atomic():
                appointment = self.appointment_model_cls.objects.create(
                    facility_name=self.facility.name,
                    timepoint_datetime=self.timepoint_datetime,
                    appt_datetime=self.appt_rdate.datetime,
                    appt_type=self.default_appt_type,
                    appt_reason=self.appt_reason or self.default_appt_reason,
                    **self.options,
                )
        except IntegrityError as e:
            raise CreateAppointmentError(
                f"An 'IntegrityError' was raised while trying to "
                f"create an appointment for subject '{self.subject_identifier}'. "
                f"Got {e}. Appointment create options were {self.options}"
            )
        return appointment

    def _update(self, appointment=None):
        """Returns an updated appointment model instance.
        """
        appointment.appt_datetime = self.appt_rdate.datetime
        appointment.timepoint_datetime = self.timepoint_datetime
        appointment.save()
        return appointment

    @property
    def appt_rdate(self):
        """Returns an arrow-object for an available appointment
        datetime.

        Raises an CreateAppointmentDateError if none.
        """
        try:
            appt_rdate = self.facility.available_rdate(
                suggested_datetime=self.suggested_datetime,
                forward_delta=self.visit.rupper,
                reverse_delta=self.visit.rlower,
                taken_datetimes=self.taken_datetimes,
            )
        except FacilityError as e:
            raise CreateAppointmentDateError(
                f"{e} Visit={repr(self.visit)}. "
                f"Try setting 'best_effort_available_datetime=True' on facility."
            )
        return appt_rdate

    @property
    def appointment_model_cls(self):
        """Returns the appointment model class.
        """
        return django_apps.get_model("edc_appointment.appointment")

    @property
    def default_appt_type(self):
        """Returns a string that is the default appointment
        type, e.g. 'clinic'.
        """
        if not self._default_appt_type:
            try:
                self._default_appt_type = settings.EDC_APPOINTMENT_DEFAULT_APPT_TYPE
            except AttributeError:
                self._default_appt_type = CLINIC
        return self._default_appt_type

    @property
    def default_appt_reason(self):
        """Returns a string that is the default appointment reason
        type, e.g. 'scheduled'.
        """
        if not self._default_appt_reason:
            try:
                self._default_appt_reason = settings.EDC_APPOINTMENT_DEFAULT_APPT_REASON
            except AttributeError:
                self._default_appt_reason = SCHEDULED_APPT
        return self._default_appt_reason
