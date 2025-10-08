from __future__ import annotations

from typing import TYPE_CHECKING

from edc_appointment.constants import INCOMPLETE_APPT
from edc_appointment.creators import (
    UnscheduledAppointmentCreator,
)
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.utils import get_related_visit_model_cls

if TYPE_CHECKING:
    from decimal import Decimal

    from edc_appointment.models import Appointment
    from edc_visit_tracking.models import SubjectVisit


def create_related_visit(appointment: Appointment, reason: str | None = None) -> SubjectVisit:
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
        # related_visit.save()
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save_base(update_fields=["appt_status"])
        appointment.refresh_from_db()
    else:
        related_visit = appointment.related_visit
    return related_visit


def get_visit_codes(model_cls: type[Appointment | SubjectVisit], order_by: str | None = None):
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
    for _ in range(0, 3):
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
