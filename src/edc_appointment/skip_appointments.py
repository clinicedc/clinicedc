from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo

from django.apps import apps as django_apps
from django.core.exceptions import FieldError
from django.db import IntegrityError
from edc_constants.constants import NOT_APPLICABLE
from edc_metadata import KEYED
from edc_metadata.utils import get_crf_metadata, get_requisition_metadata

from .constants import IN_PROGRESS_APPT, MISSED_APPT, NEW_APPT, SKIPPED_APPT
from .models import Appointment, AppointmentType
from .utils import (
    get_allow_skipped_appt_using,
    raise_on_appt_datetime_not_in_window,
    reset_appointment,
)

if TYPE_CHECKING:
    from django.db.models import QuerySet


class AnyCRF(Any):
    pass


class SkipAppointmentsError(Exception):
    pass


class SkipAppointmentsValueError(Exception):
    pass


class SkipAppointmentsFieldError(Exception):
    pass


def has_keyed_metadata(appointment) -> bool:
    """Return True if data has been submitted for this timepoint."""
    return any(
        [
            get_crf_metadata(appointment).filter(entry_status=KEYED).exists(),
            get_requisition_metadata(appointment).filter(entry_status=KEYED).exists(),
        ]
    )


class SkipAppointments:
    """Using a future date from a CRF, update the `appt_datetime` of
    the appointment that falls within the window period of the date
    AND set the `app_status` of interim appointments to `SKIPPED_APPT`.

    * CRF has a datefield which captures the date when the patient
      is next expected;
    * CRF has a charfield which captures the next visit code that is
      within the window period of the date.
    """

    def __init__(self, crf_obj: AnyCRF):
        self._last_crf_obj = None
        self._next_appt_date: date | None = None
        self._next_appt_datetime: datetime | None = None
        self._next_visit_code: str | None = None
        self._scheduled_appointments: QuerySet[Appointment] | None = None
        if not get_allow_skipped_appt_using().get(crf_obj._meta.label_lower):
            raise SkipAppointmentsError(
                "Appointments may not be skipped. "
                "settings.EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING="
                f"`{get_allow_skipped_appt_using()}`"
                f"Got model `{crf_obj._meta.label_lower}`."
            )
        self.dt_fld, self.visit_code_fld = get_allow_skipped_appt_using().get(
            crf_obj._meta.label_lower
        )
        self.crf_model_cls = django_apps.get_model(crf_obj._meta.label_lower)
        self.related_visit_model_attr: str = crf_obj.related_visit_model_attr()
        self.appointment: Appointment = getattr(
            crf_obj, self.related_visit_model_attr
        ).appointment
        self.subject_identifier: str = self.appointment.subject_identifier
        self.visit_schedule_name: str = self.appointment.visit_schedule_name
        self.schedule_name: str = self.appointment.schedule_name

    def update(self):
        """Reset appointments and set any as skipped up to the
        date provided from the CRF.
        """
        self.reset_appointments()
        self.update_appointments()

    def reset_appointments(self):
        """Reset any Appointments previously where `appt_status`
        is SKIPPED_APPT.

        Also reset `appt_datetime` on any new appts (NEW_APPT).
        """
        # reset auto-created MISSED_APPT (appt_type__isnull=True)
        # TODO: this for-loop block may be removed once all auto-created
        #    missed appts are removed.
        for appointment in self.scheduled_appointments.filter(
            appt_type__isnull=True, appt_timing=MISSED_APPT, visit_code_sequence=0
        ).exclude(
            appt_status__in=[SKIPPED_APPT, NEW_APPT],
        ):
            reset_appointment(appointment)

        # reset SKIPPED_APPT or NEW_APPT
        for appointment in self.scheduled_appointments.filter(
            appt_status__in=[SKIPPED_APPT, NEW_APPT],
        ):
            try:
                reset_appointment(appointment)
            except IntegrityError as e:
                print(e)

    def update_appointments(self):
        """Update Appointments up to n-1 using the next apointment
        date.

        Set `appt_status` = SKIPPED_APPT up to the date provided from
        the CRF.

        The `appt_datetime` for the last appointment in the sequence
        (n) will set to the date provided from the CRF and left as a
        NEW_APPT.
        .
        """
        appointment = self.appointment.next_by_timepoint
        while appointment:
            if self.update_appointment_as_next_scheduled(appointment):
                break
            else:
                self.update_appointment_as_skipped(appointment)
            appointment = appointment.next_by_timepoint

    @property
    def last_crf_obj(self):
        """Return the CRF instance for the last timepoint /
        report_datetime.
        """
        if not self._last_crf_obj:
            try:
                self._last_crf_obj = (
                    self.crf_model_cls.objects.filter(**self.query_opts)
                    .order_by(f"{self.related_visit_model_attr}__report_datetime")
                    .last()
                )
            except FieldError as e:
                raise SkipAppointmentsFieldError(
                    f"{e}. See {self.crf_model_cls._meta.label_lower}."
                )
        return self._last_crf_obj

    @property
    def next_appt_date(self) -> date | None:
        """Return the date from the CRF."""
        if not self._next_appt_date:
            try:
                self._next_appt_date = getattr(self.last_crf_obj, self.dt_fld)
            except AttributeError:
                raise SkipAppointmentsFieldError(
                    f"Unknown field name for next scheduled appointment date. See "
                    f"{self.last_crf_obj._meta.label_lower}. Got `{self.dt_fld}`."
                )
        return self._next_appt_date

    @property
    def next_appt_datetime(self) -> datetime:
        """Return a datetime representation of next_appt_date."""
        if not self._next_appt_datetime:
            self._next_appt_datetime = datetime(
                year=self.next_appt_date.year,
                month=self.next_appt_date.month,
                day=self.next_appt_date.day,
                hour=6,
                minute=0,
                tzinfo=ZoneInfo("UTC"),
            )
        return self._next_appt_datetime

    @property
    def scheduled_appointments(self) -> QuerySet[Appointment]:
        """Return a queryset of scheduled appointments for this
        subject's schedule (visit_code_sequence=0).
        """
        if not self._scheduled_appointments:
            self._scheduled_appointments = Appointment.objects.filter(
                visit_schedule_name=self.visit_schedule_name,
                schedule_name=self.schedule_name,
                visit_code_sequence=0,
                subject_identifier=self.subject_identifier,
            ).order_by("timepoint_datetime")
        return self._scheduled_appointments

    @property
    def visit_codes(self) -> list[str]:
        """Return a list of scheduled visit codes for this subject's
        schedule.
        """
        return [obj.visit_code for obj in self.scheduled_appointments]

    @property
    def next_visit_code(self) -> str:
        """Return the suggested visit_code entered on the last
        CRF instance ir raises.
        """
        if not self._next_visit_code:
            try:
                self._next_visit_code = getattr(self.last_crf_obj, self.visit_code_fld)
            except AttributeError:
                raise SkipAppointmentsFieldError(
                    "Unknown field name for visit code. See "
                    f"{self.last_crf_obj._meta.label_lower}. Got `{self.visit_code_fld}`."
                )
            if self._next_visit_code not in self.visit_codes:
                raise SkipAppointmentsValueError(
                    "Invalid value for visit code. Expected one of "
                    f"{','.join(self.visit_codes)}. See {self.last_crf_obj._meta.label_lower}."
                    f"{self.visit_code_fld}`. Got `{self._next_visit_code}`"
                )
        return self._next_visit_code

    @property
    def query_opts(self) -> dict[str, str]:
        return {
            f"{self.related_visit_model_attr}__subject_identifier": self.subject_identifier,
            f"{self.related_visit_model_attr}__visit_schedule_name": self.visit_schedule_name,
            f"{self.related_visit_model_attr}__schedule_name": self.schedule_name,
        }

    def update_appointment_as_skipped(self, appointment: Appointment) -> None:
        if appointment.appt_status in [
            NEW_APPT,
            SKIPPED_APPT,
            IN_PROGRESS_APPT,
        ] and not has_keyed_metadata(appointment):
            appointment.appt_type = AppointmentType.objects.get(name=NOT_APPLICABLE)
            appointment.appt_status = SKIPPED_APPT
            appointment.appt_timing = NOT_APPLICABLE
            appointment.comment = (
                f"based on date reported at {self.last_crf_obj.related_visit.visit_code}"
            )
            appointment.save(
                update_fields=["appt_type", "appt_status", "appt_timing", "comment"]
            )

    def update_appointment_as_next_scheduled(self, appointment: Appointment) -> bool:
        """Return True if this is the "next" appointment (the last
        appointment in the sequence).

        If "next", try to update if CRfs not yet submitted/KEYED.
        """
        is_next_scheduled_appointment = (
            appointment.visit_code == self.next_visit_code
            and appointment.visit_code_sequence == 0
        )
        if (
            is_next_scheduled_appointment
            and appointment.appt_status in [NEW_APPT, SKIPPED_APPT, IN_PROGRESS_APPT]
            and not has_keyed_metadata(appointment)
        ):
            appointment.appt_status = NEW_APPT
            appointment.appt_datetime = self.next_appt_datetime
            appointment.comment = ""
            raise_on_appt_datetime_not_in_window(appointment)
            appointment.save(update_fields=["appt_status", "appt_datetime", "comment"])
            return True
        return is_next_scheduled_appointment
