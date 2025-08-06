from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist
from edc_visit_tracking.utils import get_previous_related_visit


def update_previous_refill_end_datetime(instance):
    """Update refill_end_datetime from previous visit relative to the
    refill_start_datetime of this visit.
    """
    if previous_visit := get_previous_related_visit(
        instance.related_visit, include_interim=True
    ):
        opts = {instance.__class__.related_visit_model_attr(): previous_visit}
        try:
            obj = instance.__class__.objects.get(**opts)
        except ObjectDoesNotExist:
            pass
        else:
            obj.refill_end_datetime = instance.refill_start_datetime - relativedelta(seconds=1)
            obj.save_base(update_fields=["refill_end_datetime"])


__all__ = ["update_previous_refill_end_datetime"]
