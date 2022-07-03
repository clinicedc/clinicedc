from .refill_creator import RefillCreator


def create_refill(instance):
    """Creates the refill for this visit, if not already created.

    Called from signal.
    """
    number_of_days = 0
    if instance.subject_visit.appointment.next:
        number_of_days = (
            instance.subject_visit.appointment.next.appt_datetime
            - instance.subject_visit.appointment.appt_datetime
        ).days
    RefillCreator(
        subject_identifier=instance.subject_visit.subject_identifier,
        refill_date=instance.refill_date,
        visit_code=instance.subject_visit.appointment.visit_code,
        visit_code_sequence=instance.subject_visit.appointment.visit_code_sequence,
        number_of_days=number_of_days,
        dosage_guideline=instance.dosage_guideline,
        formulation=instance.formulation,
        roundup_divisible_by=instance.roundup_divisible_by,
        make_active=True,
    )
