from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.utils import IntegrityError
from django.utils.timezone import is_naive
from edc_facility.facility import Facility, FacilityError
from edc_sites.valid_site_for_subject_or_raise import valid_site_for_subject_or_raise
from edc_visit_schedule.utils import is_baseline

from ..constants import SCHEDULED_APPT
from ..utils import (
    get_appointment_type_model_cls,
    get_appt_reason_default,
    get_appt_type_default,
)

if TYPE_CHECKING:
    from ..models import Appointment, AppointmentType


class CreateAppointmentError(Exception):
    pass


class CreateAppointmentDateError(Exception):
    pass


class AppointmentCreatorError(Exception):
    pass


if TYPE_CHECKING:
    from edc_visit_schedule.visit import Visit


class AppointmentCreator:
    def __init__(
        self,
        timepoint_datetime: datetime = None,
        timepoint: Decimal | None = None,
        visit: Visit | None = None,  # from edc_visit_schedule
        visit_code_sequence: int | None = None,
        facility: Facility | None = None,
        appointment_model: str = None,
        taken_datetimes: list[datetime] | None = None,
        subject_identifier: str = None,
        visit_schedule_name: str = None,
        schedule_name: str = None,
        default_appt_type: str | None = None,
        default_appt_reason: str | None = None,
        appt_status: str | None = None,
        appt_reason: str | None = None,
        suggested_datetime: datetime | None = None,
        skip_baseline: bool | None = None,
        ignore_window_period: bool | None = None,
    ):
        self._appointment = None
        self._appointment_model_cls = None
        self._default_appt_type = default_appt_type
        self._default_appt_reason = default_appt_reason
        self.skip_baseline = skip_baseline
        self.subject_identifier = subject_identifier
        self.visit_schedule_name = visit_schedule_name
        self.schedule_name: str = schedule_name
        self.appt_status = appt_status
        self.appt_reason = appt_reason
        self.appointment_model = appointment_model
        # already taken appt_datetimes for this subject
        self.taken_datetimes = taken_datetimes or []
        self.visit = visit
        self.visit_code_sequence = visit_code_sequence or 0
        self.timepoint = timepoint or self.visit.timepoint
        self.ignore_window_period = ignore_window_period
        if not isinstance(self.timepoint, Decimal):
            self.timepoint = Decimal(str(self.timepoint))

        try:
            if is_naive(timepoint_datetime):
                raise ValueError(
                    f"Naive datetime not allowed. {repr(self)}. " f"Got {timepoint_datetime}"
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
                f"Naive datetime not allowed. {repr(self)}. " f"Got {suggested_datetime}"
            )
        else:
            self.suggested_datetime = suggested_datetime or self.timepoint_datetime
        self.facility = facility or visit.facility
        if not self.facility:
            raise AppointmentCreatorError(f"facility_name not defined. See {repr(visit)}")
        self.get_appointment()

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(subject_identifier={self.subject_identifier}, "
            f"visit_code={self.visit.code}.{self.visit_code_sequence}@{int(self.timepoint)})"
        )

    def __str__(self):
        return self.subject_identifier

    def get_appointment(self) -> Appointment:
        return self.appointment

    @property
    def appointment(self) -> Appointment:
        """Returns a newly created or updated appointment model instance."""
        if not self._appointment:
            try:
                self._appointment = self.appointment_model_cls.objects.get(**self.options)
            except ObjectDoesNotExist:
                self._appointment = self._create()
            else:
                self._appointment = self._update(appointment=self._appointment)
        return self._appointment

    @property
    def options(self) -> dict:
        """Returns default options to "get" an existing
        appointment model instance.
        """
        options = dict(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule_name,
            schedule_name=self.schedule_name,
            visit_code=self.visit.code,
            visit_code_sequence=self.visit_code_sequence,
            timepoint=self.timepoint,
        )
        if self.appt_status:
            options.update(appt_status=self.appt_status)
        return options

    def _create(self) -> Appointment:
        """Returns a newly created appointment model instance."""
        valid_site_for_subject_or_raise(self.options.get("subject_identifier"))
        try:
            with transaction.atomic():
                appointment = self.appointment_model_cls.objects.create(
                    facility_name=self.facility.name,
                    timepoint_datetime=self.timepoint_datetime,
                    appt_datetime=self.appt_datetime,
                    appt_type=self.default_appt_type,
                    appt_reason=self.appt_reason or self.default_appt_reason,
                    ignore_window_period=self.ignore_window_period or False,
                    **self.options,
                )
        except IntegrityError as e:
            raise CreateAppointmentError(
                f"An 'IntegrityError' was raised while trying to "
                f"create an appointment for subject '{self.subject_identifier}'. "
                f"Got {e}. Appointment create options were {self.options}"
            )
        return appointment

    def _update(self, appointment=None) -> Appointment:
        """Returns an updated appointment model instance."""
        if is_baseline(instance=appointment) and self.skip_baseline:
            pass
        else:
            appointment.appt_datetime = self.appt_datetime
            appointment.timepoint_datetime = self.timepoint_datetime
            appointment.save()
            appointment.refresh_from_db()
        return appointment

    @property
    def appt_datetime(self) -> datetime:
        """Returns an available appointment datetime.

        Raises an CreateAppointmentDateError if none.

        Returns an unadjusted suggested datetime if this is an
        unscheduled appointment.
        """
        if self.visit_code_sequence == 0 or self.visit_code_sequence is None:
            try:
                arw = self.facility.available_arr(
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
        else:
            return self.suggested_datetime
        return arw.datetime

    @property
    def appointment_model_cls(self) -> Appointment:
        """Returns the appointment model class."""
        return django_apps.get_model("edc_appointment.appointment")

    @property
    def default_appt_type(self) -> AppointmentType | None:
        """Returns an AppointmentType instance or None for
        the default appointment type, e.g. 'clinic'.
        """
        if not self._default_appt_type:
            try:
                self._default_appt_type = get_appointment_type_model_cls().objects.get(
                    name=get_appt_type_default()
                )
            except ObjectDoesNotExist:
                self._default_appt_type = None
        return self._default_appt_type

    @property
    def default_appt_reason(self) -> str:
        """Returns a string that is the default appointment reason
        type, e.g. 'scheduled'.
        """
        if not self._default_appt_reason:
            try:
                self._default_appt_reason = get_appt_reason_default()
            except AttributeError:
                self._default_appt_reason = SCHEDULED_APPT
        return self._default_appt_reason
