from __future__ import annotations

from collections.abc import Iterable

from django.apps import apps as django_apps

from ..choices import STOCK_TRANSACTION_ABBR


def last_txn_abbr_by_stock(stock_ids: Iterable) -> dict:
    """Map stock_id -> abbreviation of its most recent transaction_type.

    One query for all given stocks; the first row per stock (ordered by
    descending datetime) is the latest. Stocks with no ledger rows, and falsy
    ids, are omitted. Abbreviations come from ``STOCK_TRANSACTION_ABBR`` so the
    stock take discrepancy report and its PDF stay in sync.
    """
    ids = [stock_id for stock_id in stock_ids if stock_id]
    if not ids:
        return {}
    stock_transaction_cls = django_apps.get_model("edc_pharmacy.stocktransaction")
    last_type: dict = {}
    for stock_id, txn_type in (
        stock_transaction_cls.objects.filter(stock_id__in=ids)
        .order_by("stock_id", "-transaction_datetime")
        .values_list("stock_id", "transaction_type")
    ):
        last_type.setdefault(stock_id, txn_type)
    return {
        stock_id: STOCK_TRANSACTION_ABBR.get(txn_type, "")
        for stock_id, txn_type in last_type.items()
    }
