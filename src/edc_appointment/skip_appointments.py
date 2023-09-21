from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from edc_constants.constants import NOT_APPLICABLE

from .constants import MISSED_APPT, NEW_APPT, SKIPPED_APPT
from .models import Appointment, AppointmentType
from .utils import (
    InvalidModelForSkippedAppts,
    get_allow_skipped_appt_using,
    reset_appointment,
)

if TYPE_CHECKING:
    from edc_visit_schedule.models import VisitSchedule


class AnyCRF(Any):
    pass


class SkipAppointmentsError(Exception):
    pass


class SkipAppointments:
    def __init__(self, obj: AnyCRF):
        try:
            self.model, self.field_name = get_allow_skipped_appt_using(obj)
        except InvalidModelForSkippedAppts:
            raise SkipAppointmentsError(
                "Appointments may not be skipped. "
                "settings.EDC_APPOINTMENT_ALLOW_SKIPPED_APPT_USING="
                f"`{get_allow_skipped_appt_using()}`"
                f"Got model `{obj._meta.label_lower}`."
            )
        self._last_next_appointment = None
        self._next_visit_code: str | None = None
        self.obj = obj
        self.model_cls = django_apps.get_model(self.model)
        self.related_visit_model_attr: str = obj.related_visit_model_attr()
        self.appointment: Appointment = getattr(
            self.obj, self.related_visit_model_attr
        ).appointment
        self.subject_identifier: str = self.appointment.subject_identifier
        self.visit_schedule_name: str = self.appointment.visit_schedule_name
        self.schedule_name: str = self.appointment.schedule_name
        self.next_appt_date: date = getattr(self.last_next_appointment, self.field_name)
        self.next_appt_datetime = datetime(
            year=self.next_appt_date.year,
            month=self.next_appt_date.month,
            day=self.next_appt_date.day,
            hour=8,
            minute=0,
            tzinfo=ZoneInfo("utc"),
        )
        self.skip_to_next()

    def skip_to_next(self):
        """Resets appointments and sets any as skipped until the
        `next_appt_date`.
        """
        if self.next_visit_code:
            self.reset_skipped()
            self.update_to_next()

    def reset_skipped(self):
        """Reset any Appointments previously where `appt_status`
        is SKIPPED_APPT.

        Also reset `appt_datetime` on any new appts (NEW_APPT).
        """

        for appointment in Appointment.objects.filter(
            visit_schedule_name=self.visit_schedule_name,
            schedule_name=self.schedule_name,
            appt_type__isnull=True,
            appt_timing=MISSED_APPT,
            subject_identifier=self.subject_identifier,
        ).exclude(
            appt_status__in=[SKIPPED_APPT, NEW_APPT],
        ):
            reset_appointment(appointment)

        for appointment in Appointment.objects.filter(
            visit_schedule_name=self.visit_schedule_name,
            schedule_name=self.schedule_name,
            appt_status__in=[SKIPPED_APPT, NEW_APPT],
            subject_identifier=self.subject_identifier,
        ):
            try:
                reset_appointment(appointment)
            except IntegrityError as e:
                print(e)

    def update_to_next(self):
        """Update Appointments, set `appt_status` = SKIPPED_APPT until
        the found "next" appointment.
        """
        appointment = self.appointment.next_by_timepoint
        while appointment:
            if self.update_appointment_as_next(appointment):
                break
            else:
                self.update_appointment_as_skipped(appointment)
            appointment = appointment.next_by_timepoint

    @property
    def last_next_appointment(self):
        if not self._last_next_appointment:
            self._last_next_appointment = (
                self.model_cls.objects.filter(**self.query_opts)
                .order_by(self.field_name)
                .last()
            )
        return self._last_next_appointment

    @property
    def next_visit_code(self):
        if not self._next_visit_code:
            try:
                visit_schedule_obj: VisitSchedule = self.last_next_appointment.visitschedule
            except (AttributeError, ObjectDoesNotExist):
                self._next_visit_code = None
            else:
                self._next_visit_code = visit_schedule_obj.visit_code
        return self._next_visit_code

    @property
    def query_opts(self):
        return {
            f"{self.related_visit_model_attr}__subject_identifier": self.subject_identifier,
            f"{self.related_visit_model_attr}__visit_schedule_name": self.visit_schedule_name,
            f"{self.related_visit_model_attr}__schedule_name": self.schedule_name,
        }

    def update_appointment_as_next(self, appointment):
        if self.is_next_appointment(appointment) and appointment.appt_status in [
            NEW_APPT,
            SKIPPED_APPT,
        ]:
            appointment.appt_status = NEW_APPT
            appointment.appt_datetime = self.next_appt_datetime
            appointment.comment = ""
            appointment.save(update_fields=["appt_status", "appt_datetime", "comment"])
            return True
        return self.is_next_appointment(appointment)

    def is_next_appointment(self, appointment: Appointment):
        """Return True if this is the appointment reported as the
        subject's next appointment.

        Match on visit_code.
        """
        return (
            appointment.visit_code == self.next_visit_code
            and appointment.visit_code_sequence == 0
        )

    def update_appointment_as_skipped(self, appointment: Appointment):
        if appointment.appt_status in [NEW_APPT, SKIPPED_APPT]:
            appointment.appt_type = AppointmentType.objects.get(name=NOT_APPLICABLE)
            appointment.appt_status = SKIPPED_APPT
            appointment.appt_timing = NOT_APPLICABLE
            appointment.comment = (
                "based on date reported at "
                f"{self.last_next_appointment.related_visit.visit_code}"
            )
            appointment.save(
                update_fields=["appt_type", "appt_status", "appt_timing", "comment"]
            )
