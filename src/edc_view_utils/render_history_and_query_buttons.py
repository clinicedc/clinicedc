from __future__ import annotations

from typing import TYPE_CHECKING

from .history_button import HistoryButton
from .query_button import QueryButton

if TYPE_CHECKING:
    from edc_appointment.models import Appointment
    from edc_metadata.models import CrfMetadata
    from edc_registration.models import RegisteredSubject
    from edc_visit_schedule.models import VisitSchedule

__all__ = ["render_history_and_query_buttons"]


def render_history_and_query_buttons(
    context,
    model_obj: CrfMetadata = None,
    appointment: Appointment = None,
    registered_subject: RegisteredSubject = None,
    visit_schedule: VisitSchedule = None,
) -> tuple[HistoryButton, QueryButton]:
    # if still using deprecated ModelWrapper, get model instance
    # from model_wrapper
    appointment = getattr(appointment, "object", appointment)
    query_btn = QueryButton(
        metadata_model_obj=model_obj,
        user=context["request"].user,
        current_site=context["request"].site,
        appointment=appointment,
        registered_subject=registered_subject,
        visit_schedule=visit_schedule,
    )
    history_btn = HistoryButton(model_obj=model_obj)
    return history_btn, query_btn
