from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..create_refill import create_refill

if TYPE_CHECKING:
    from ...models import RxRefill


def calculate_days_to_next_refill(refill) -> int:
    """Returns the number of days until medication runs out"""
    return 0


def create_refills_from_crf(instance: Any, related_visit_model_attr: str) -> RxRefill:
    subject_visit = getattr(instance, related_visit_model_attr)
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
    return rx_refill
