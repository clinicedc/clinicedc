from ..models import RxRefill


def delete_next_refill(instance):
    if qs := RxRefill.objects.filter(
        rx__subject_identifier=instance.subject_visit.subject_identifier,
        refill_date__gt=instance.refill_date or instance.report_datetime,
        active=False,
    ).order_by("refill_date"):
        qs[0].delete()
