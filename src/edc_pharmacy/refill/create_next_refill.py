from .refill_creator import RefillCreator


def create_next_refill(instance):
    """Creates the next refill relative to the current visit,
    if not already created.

    Called from signal.
    """
    if instance.subject_visit.appointment.next:
        number_of_days = 0
        if instance.subject_visit.appointment.next.next:
            number_of_days = (
                instance.subject_visit.appointment.next.next.appt_datetime
                - instance.subject_visit.appointment.next.appt_datetime
            ).days
        RefillCreator(
            subject_identifier=instance.subject_visit.subject_identifier,
            refill_date=instance.subject_visit.appointment.next.appt_datetime,
            visit_code=instance.subject_visit.appointment.next.visit_code,
            visit_code_sequence=instance.subject_visit.appointment.next.visit_code_sequence,
            number_of_days=number_of_days,
            dosage_guideline=instance.next_dosage_guideline,
            formulation=instance.next_formulation,
            make_active=False,
        )
