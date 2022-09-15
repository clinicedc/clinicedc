from __future__ import annotations

from typing import Any

from .refill_creator import RefillCreator, RefillCreatorError


def create_next_refill(instance: Any, related_visit_model_attr: str) -> Any | None:
    """Creates the next refill relative to the current visit,
    if not already created.

    Called from signal.

    Instance should be a subclass of StudyMedicationCrfModelMixin
    """
    rx_refill = None
    if not getattr(instance, "creates_refills_from_crf", None):
        raise RefillCreatorError("Expected an instance of StudyMedicationCrfModelMixin")
    next_next_appointment = getattr(instance, related_visit_model_attr).appointment.next.next
    if next_next_appointment:
        refill_creator = RefillCreator(
            dosage_guideline=instance.next_dosage_guideline,
            formulation=instance.next_formulation,
            make_active=False,
            refill_start_datetime=instance.refill_end_datetime,
            refill_end_datetime=next_next_appointment.appt_datetime,
            roundup_divisible_by=instance.roundup_divisible_by,
            subject_identifier=getattr(instance, related_visit_model_attr).subject_identifier,
            weight_in_kgs=getattr(instance, "weight_in_kgs", None),
        )
        rx_refill = refill_creator.rx_refill
    return rx_refill
