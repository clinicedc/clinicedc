from ..models import RxRefill
from .refill_creator import RefillCreator


def create_next_refill(instance):
    """Creates the next refill relative to the current visit,
    if not already created.

    Called from signal.
    """
    if (
        RxRefill.objects.filter(
            rx__subject_identifier=instance.subject_visit.subject_identifier,
            visit_code=instance.subject_visit.visit_code,
            visit_code_sequence=instance.subject_visit.visit_code_sequence,
        ).exists()
        and instance.subject_visit.appointment.next
    ):
        number_of_days = 0
        if instance.subject_visit.appointment.next.next:
            number_of_days = (
                instance.subject_visit.appointment.next.next.appt_datetime
                - instance.subject_visit.appointment.next.appt_datetime
            ).days

        RefillCreator(
            dosage_guideline=instance.next_dosage_guideline,
            formulation=instance.next_formulation,
            make_active=False,
            number_of_days=number_of_days,
            refill_date=instance.subject_visit.appointment.next.appt_datetime,
            roundup_divisible_by=instance.roundup_divisible_by,
            subject_identifier=instance.subject_visit.subject_identifier,
            visit_code=instance.subject_visit.appointment.next.visit_code,
            visit_code_sequence=instance.subject_visit.appointment.next.visit_code_sequence,
            weight_in_kgs=getattr(instance, "weight_in_kgs", None),
        )
