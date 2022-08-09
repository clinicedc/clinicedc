from .refill_creator import RefillCreator


def create_refill(instance) -> RefillCreator:
    """Creates the refill for this visit, if not already created.

    Called from signal.
    """
    number_of_days = 0
    if instance.subject_visit.appointment.next:
        number_of_days = (
            instance.subject_visit.appointment.next.appt_datetime
            - instance.subject_visit.appointment.appt_datetime
        ).days
    return RefillCreator(
        dosage_guideline=instance.dosage_guideline,
        formulation=instance.formulation,
        make_active=True,
        number_of_days=number_of_days,
        refill_date=instance.refill_date,
        roundup_divisible_by=instance.roundup_divisible_by,
        subject_identifier=instance.subject_visit.subject_identifier,
        visit_code=instance.subject_visit.appointment.visit_code,
        visit_code_sequence=instance.subject_visit.appointment.visit_code_sequence,
        weight_in_kgs=getattr(instance, "weight_in_kgs", None),
    )
