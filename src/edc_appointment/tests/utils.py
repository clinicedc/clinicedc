from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Type

from edc_appointment.constants import IN_PROGRESS_APPT, INCOMPLETE_APPT
from edc_appointment.creators import (
    UnscheduledAppointmentCreator,
    create_unscheduled_appointment,
)
from edc_appointment.utils import get_appointment_model_cls
from edc_visit_tracking.constants import SCHEDULED, UNSCHEDULED
from edc_visit_tracking.utils import get_related_visit_model_cls

if TYPE_CHECKING:
    from decimal import Decimal

    from edc_appointment.models import Appointment
    from edc_visit_tracking.models import SubjectVisit


def get_appointment(
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
        appointment = create_unscheduled_appointment(appointment)
    appointment.appt_status = IN_PROGRESS_APPT
    appointment.save()
    appointment.refresh_from_db()
    return appointment


def create_related_visit(
    appointment: Appointment, reason: str | None = None
) -> SubjectVisit:
    if not appointment.related_visit:
        related_visit = get_related_visit_model_cls().objects.create(
            appointment=appointment,
            subject_identifier=appointment.subject_identifier,
            report_datetime=appointment.appt_datetime,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            visit_code_sequence=appointment.visit_code_sequence,
            reason=reason or SCHEDULED,
        )
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save_base(update_fields=["appt_status"])
        appointment.refresh_from_db()
    else:
        related_visit = appointment.related_visit
    return related_visit


def get_visit_codes(model_cls: Type[Appointment | SubjectVisit], order_by: str = None):
    return [
        f"{o.visit_code}.{o.visit_code_sequence}"
        for o in model_cls.objects.all().order_by(order_by)
    ]


def get_timepoint_from_visit_code(
    instance,
    visit_code: str,
) -> float | Decimal | None:
    timepoint = None
    for v in instance.schedule.visits.timepoints:
        if v.name == visit_code:
            timepoint = v.timepoint
            break
    return timepoint


def create_unscheduled_appointments(appointment):
    for i in range(0, 3):
        creator = UnscheduledAppointmentCreator(
            subject_identifier=appointment.subject_identifier,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            suggested_visit_code_sequence=appointment.visit_code_sequence + 1,
        )
        appointment = creator.appointment
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save_base(update_fields=["appt_status"])
