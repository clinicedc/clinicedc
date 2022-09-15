from typing import Any

from edc_constants.constants import YES

from ..create_next_refill import create_next_refill
from ..create_refill import create_refill
from .delete_next_refills_for_crf import delete_next_refills_for_crf


def calculate_days_to_next_refill(refill) -> int:
    """Returns the number of days until medication runs out"""
    return 0


def create_refills_from_crf(instance: Any, visit_model_attr: str) -> tuple:
    next_rx_refill = None
    subject_visit = getattr(instance, visit_model_attr)
    rx_refill = create_refill(
        refill_identifier=instance.refill_identifier,
        subject_identifier=subject_visit.subject_identifier,
        dosage_guideline=instance.dosage_guideline,
        formulation=instance.formulation,
        refill_start_datetime=instance.refill_start_datetime,
        refill_end_datetime=instance.refill_end_datetime,
        roundup_divisible_by=instance.roundup_divisible_by,
        weight_in_kgs=getattr(instance, "weight_in_kgs", None),
    )
    if instance.order_or_update_next == YES:
        next_rx_refill = create_next_refill(instance, visit_model_attr)
    elif not getattr(instance, visit_model_attr).appointment.next:
        delete_next_refills_for_crf(instance)
    return rx_refill, next_rx_refill
