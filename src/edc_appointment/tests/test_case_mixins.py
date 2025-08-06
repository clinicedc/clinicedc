from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from edc_visit_tracking.constants import UNSCHEDULED

from ..constants import IN_PROGRESS_APPT, INCOMPLETE_APPT
from ..creators import UnscheduledAppointmentCreator
from ..utils import get_appointment_model_cls

if TYPE_CHECKING:
    from edc_appointment.models import Appointment


class AppointmentTestCaseMixin:
    def get_timepoint_from_visit_code(
        self: Any,
        instance: Any,
        visit_code: str,
    ) -> float | Decimal | None:
        timepoint = None
        for v in instance.schedule.visits.timepoints:
            if v.name == visit_code:
                timepoint = v.timepoint
                break
        return timepoint

    def get_appointment(
        self,
        subject_identifier: str | None = None,
        visit_code: str | None = None,
        visit_code_sequence: int | None = None,
        reason: str | None = None,
        appt_datetime: datetime | None = None,
        timepoint: float | Decimal | None = None,
    ) -> Appointment:
        if timepoint is not None:
            appointment = get_appointment_model_cls().objects.get(
                subject_identifier=subject_identifier,
                timepoint=timepoint,
                visit_code_sequence=visit_code_sequence,
            )
        else:
            appointment = get_appointment_model_cls().objects.get(
                subject_identifier=subject_identifier,
                visit_code=visit_code,
                visit_code_sequence=visit_code_sequence,
            )
        if appt_datetime:
            appointment.appt_datetime = appt_datetime
            appointment.save()
            appointment.refresh_from_db()
        if reason == UNSCHEDULED:
            appointment = self.create_unscheduled_appointment(appointment)
        appointment.appt_status = IN_PROGRESS_APPT
        appointment.save()
        appointment.refresh_from_db()
        return appointment

    @staticmethod
    def create_unscheduled_appointment(appointment: Appointment) -> Appointment:
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save()
        appointment.refresh_from_db()
        appt_creator = UnscheduledAppointmentCreator(
            subject_identifier=appointment.subject_identifier,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            suggested_visit_code_sequence=appointment.visit_code_sequence + 1,
            facility=appointment.facility,
        )
        return appt_creator.appointment
