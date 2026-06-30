from __future__ import annotations

from collections.abc import Iterable

from django.apps import apps as django_apps


def subject_identifier_by_stock(stock_ids: Iterable) -> dict:
    """Map stock_id -> recipient subject_identifier from the Allocation table.

    The Allocation table is the canonical record of who a stock item was
    allocated to (``Allocation.subject_identifier`` is stamped from
    ``registered_subject`` on save). This is robust where the
    ``Stock.subject_identifier`` cache is unpopulated and where the
    ``Stock.allocation`` sticky-pointer FK is null (e.g. terminal/dispensed
    stock). The most recent allocation per stock wins; falsy ids are skipped.
    """
    ids = [stock_id for stock_id in stock_ids if stock_id]
    if not ids:
        return {}
    allocation_cls = django_apps.get_model("edc_pharmacy.allocation")
    result: dict = {}
    for stock_id, subject_identifier in (
        allocation_cls.objects.filter(stock_id__in=ids)
        .order_by("stock_id", "-allocation_datetime")
        .values_list("stock_id", "subject_identifier")
    ):
        result.setdefault(stock_id, subject_identifier)
    return result
