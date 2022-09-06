from __future__ import annotations

from datetime import datetime
from typing import Any

from .refill_creator import RefillCreator


def create_refill(
    refill_identifier: str,
    subject_identifier: str,
    dosage_guideline: Any,
    formulation: Any,
    refill_start_datetime: datetime,
    refill_end_datetime: datetime,
    roundup_divisible_by: int | None,
    weight_in_kgs: float | None,
) -> RefillCreator:
    """Creates the edc_pharmacy refill for this study medication CRF,
    if not already created.

    Usually called by study medication CRF

    Called from signal.
    """
    rx_refill = RefillCreator(
        refill_identifier=refill_identifier,
        dosage_guideline=dosage_guideline,
        formulation=formulation,
        make_active=True,
        refill_start_datetime=refill_start_datetime,
        refill_end_datetime=refill_end_datetime,
        roundup_divisible_by=roundup_divisible_by,
        subject_identifier=subject_identifier,
        weight_in_kgs=weight_in_kgs,
    )
    # adjust_previous

    return rx_refill
