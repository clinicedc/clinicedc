from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from django.core.exceptions import ObjectDoesNotExist

from ..utils import get_rxrefill_model_cls
from .refill_creator import RefillCreator

if TYPE_CHECKING:
    from ..models import DosageGuideline, Formulation, RxRefill


def create_refill(
    refill_identifier: str,
    subject_identifier: str,
    dosage_guideline: DosageGuideline,
    formulation: Formulation,
    refill_start_datetime: datetime,
    refill_end_datetime: datetime,
    roundup_divisible_by: int | None,
    weight_in_kgs: float | None,
) -> RxRefill:
    """Creates or updated the edc_pharmacy refill for this study medication CRF,
    if not already created.

    Usually called by study medication CRF

    Called from signal.
    """
    rx_refill = None
    creator = None
    try:
        rx_refill = get_rxrefill_model_cls().objects.get(refill_identifier=refill_identifier)
    except ObjectDoesNotExist:
        creator = RefillCreator(
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
    else:
        rx_refill.dosage_guideline = dosage_guideline
        rx_refill.formulation = formulation
        rx_refill.refill_start_datetime = refill_start_datetime
        rx_refill.refill_end_datetime = refill_end_datetime
        rx_refill.roundup_divisible_by = roundup_divisible_by
        rx_refill.weight_in_kgs = weight_in_kgs
        rx_refill.save()
        rx_refill.refresh_from_db()
    return rx_refill or creator.rx_refill
