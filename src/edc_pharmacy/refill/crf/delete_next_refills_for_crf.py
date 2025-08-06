from ...utils import get_rxrefill_model_cls


def delete_next_refills_for_crf(instance):
    if (
        qs := get_rxrefill_model_cls()
        .objects.filter(
            rx__subject_identifier=instance.subject_visit.subject_identifier,
            refill_start_datetime__gt=instance.refill_start_datetime,
            active=False,
        )
        .order_by("refill_start_datetime")
    ):
        qs[0].delete()
