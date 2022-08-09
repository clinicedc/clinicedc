from edc_constants.constants import YES

from ..exceptions import RefillAlreadyExists
from .create_next_refill import create_next_refill
from .create_refill import create_refill
from .delete_next_refill import delete_next_refill


def calculate_days_to_next_refill(refill) -> int:
    """Returns the number of days until medication runs out"""
    return 0


def create_refills_from_crf(instance):
    try:
        refill_creator = create_refill(instance)
    except RefillAlreadyExists:
        pass
    else:
        instance.days_to_next_refill = calculate_days_to_next_refill(
            refill_creator.refill.total
        )
        instance.save_base(update_fields=["days_to_next_refill"])
    if instance.order_next == YES:
        try:
            create_next_refill(instance)
        except RefillAlreadyExists:
            pass
    elif not instance.subject_visit.appointment.next:
        delete_next_refill(instance)
