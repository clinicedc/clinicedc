from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo

from django.apps import apps as django_apps
from django.core.exceptions import FieldError
from django.db import IntegrityError
from edc_metadata.utils import has_keyed_metadata

from .constants import MISSED_APPT, NEW_APPT, SKIPPED_APPT
from .exceptions import AppointmentWindowError
from .models import Appointment
from .utils import (
    AppointmentAlreadyStarted,
    get_allow_skipped_appt_using,
    get_appointment_by_datetime,
    raise_on_appt_datetime_not_in_window,
    reset_appointment,
    skip_appointment,
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


class SkipAppointments:
    """Using a future date from a CRF, update the `appt_datetime` of
    the appointment that falls within the window period of the date
    AND set the `app_status` of interim appointments to `SKIPPED_APPT`.

    * CRF has a datefield which captures the date when the patient
      is next expected;
    * CRF has a charfield which captures the next visit code that is
      within the window period of the date.
    * You should validate the next visit code and the date before
      calling (e.g. on the form).
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
        self.crf_obj = crf_obj
        self.dt_fld, self.visit_code_fld = get_allow_skipped_appt_using().get(
            self.crf_obj._meta.label_lower
        )
        self.crf_model_cls = django_apps.get_model(self.crf_obj._meta.label_lower)
        self.related_visit_model_attr: str = self.crf_obj.related_visit_model_attr()
        self.appointment: Appointment = getattr(
            self.crf_obj, self.related_visit_model_attr
        ).appointment
        self.subject_identifier: str = self.appointment.subject_identifier
        self.visit_schedule_name: str = self.appointment.visit_schedule_name
        self.schedule_name: str = self.appointment.schedule_name

    def update(self) -> bool:
        """Reset appointments and set any as skipped up to the
        date provided from the CRF.

        Return True if next scheduled appointment is updated.
        """
        self.reset_appointments()
        return self.update_appointments()

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
            try:
                reset_appointment(appointment)
            except AppointmentAlreadyStarted:
                pass

        for appointment in self.scheduled_appointments.filter(
            appt_datetime__gt=self.appointment.appt_datetime,
        ):
            try:
                reset_appointment(appointment)
            except IntegrityError as e:
                print(e)
            except AppointmentAlreadyStarted:
                pass

    def update_appointments(self) -> bool:
        """Return True if next scheduled appointment is updated.

        Update Appointments up the next apointment date.

        Set `appt_status` = SKIPPED_APPT up the appointment BEFORE
        the date from the CRF.

        Only set the `appt_datetime` for the appointment where the  date
        from the CRF lands in the window period. Leave status as NEW_APPT.

        Stop if any appointment has keyed data.
        """
        next_scheduled_appointment_updated = False
        skip_comment = (
            f"based on date reported at {self.last_crf_obj.related_visit.visit_code}"
        )

        cancelled_appointments = []
        appointment = self.appointment
        while appointment:
            if appointment.visit_code_sequence > 0:
                if appointment.appt_status == NEW_APPT:
                    cancelled_appointments.append(appointment)
            elif self.is_next_scheduled(appointment):
                try:
                    self.update_appointment_as_next_scheduled(appointment)
                except AppointmentAlreadyStarted:
                    pass
                else:
                    next_scheduled_appointment_updated = True
                break
            else:
                try:
                    skip_appointment(appointment, comment=skip_comment)
                except AppointmentAlreadyStarted:
                    pass
            appointment = appointment.relative_next
        for appointment in cancelled_appointments:
            appointment.delete()
        return next_scheduled_appointment_updated

    def is_next_scheduled(self, appointment):
        return (
            appointment.visit_code == self.next_visit_code
            and appointment.visit_code_sequence == 0
        )

    def update_appointment_as_next_scheduled(self, appointment: Appointment) -> None:
        """Return True if this is the "next" appointment (the last
        appointment in the sequence).

        If "next", try to update if CRfs not yet submitted/KEYED.
        """
        if has_keyed_metadata(appointment) or appointment.related_visit:
            raise AppointmentAlreadyStarted(
                f"Unable update as next. Appointment already started. Got {appointment}."
            )
        else:
            appointment.appt_status = NEW_APPT
            appointment.appt_datetime = self.next_appt_datetime
            appointment.comment = ""
            self.validate_appointment_as_next(appointment)
            appointment.save(update_fields=["appt_status", "appt_datetime", "comment"])

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
    def query_opts(self) -> dict[str, str]:
        return {
            f"{self.related_visit_model_attr}__subject_identifier": self.subject_identifier,
            f"{self.related_visit_model_attr}__visit_schedule_name": self.visit_schedule_name,
            f"{self.related_visit_model_attr}__schedule_name": self.schedule_name,
        }

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
            self._next_visit_code = getattr(
                self._next_visit_code, "visit_code", self._next_visit_code
            )
            if self._next_visit_code not in self.visit_codes:
                raise SkipAppointmentsValueError(
                    "Invalid value for visit code. Expected one of "
                    f"{','.join(self.visit_codes)}. See {self.last_crf_obj._meta.label_lower}."
                    f"{self.visit_code_fld}`. Got `{self._next_visit_code}`"
                )
        return self._next_visit_code

    def validate_appointment_as_next(self, appointment):
        try:
            raise_on_appt_datetime_not_in_window(appointment)
        except AppointmentWindowError as e:
            raise SkipAppointmentsValueError(e)

        next_appt = get_appointment_by_datetime(
            self.next_appt_datetime,
            appointment.subject_identifier,
            appointment.visit_schedule_name,
            appointment.schedule_name,
            raise_if_in_gap=False,
        )
        if next_appt.visit_code != self.next_visit_code:
            raise SkipAppointmentsValueError(
                "Visit code is invalid for appointment datetime. "
                f"You suggested {self.next_visit_code}. "
                f"The appointment datetime matches with {next_appt.visit_code}."
            )

        next_appointment = get_appointment_by_datetime(
            self.next_appt_datetime,
            appointment.subject_identifier,
            appointment.visit_schedule_name,
            appointment.schedule_name,
            raise_if_in_gap=False,
        )
        return self.appointment == next_appointment

        # and getattr(
        #     self.crf_obj, "allow_create_interim", None
        # ):
        #         subject_identifier=self.appointment.subject_identifier,
        #         visit_schedule_name=self.appointment.visit_schedule_name,
        #         schedule_name=self.appointment.schedule_name,
        #         timepoint=self.appointment.timepoint,
        #         visit_code=self.appointment.visit_code,
        #         visit_code_sequence=self.appointment.visit_code_sequence + 1,
        #         facility=self.appointment.facility,
        #     )
