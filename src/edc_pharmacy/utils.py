from __future__ import annotations

from typing import TYPE_CHECKING

from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_visit_tracking.utils import get_previous_related_visit

if TYPE_CHECKING:
    from edc_pharmacy.models import Container, Stock


def get_rxrefill_model_cls():
    return django_apps.get_model("edc_pharmacy.rxrefill")


def get_rx_model_cls():
    return django_apps.get_model("edc_pharmacy.rx")


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


def repackage_stock(stock: Stock, container: Container) -> Stock:
    """Take from stock and fill container as new stock item"""
    stock.unit_qty_out = stock.unit_qty_out + container.qty
    stock.save(update_fields=["unit_qty_out"])
    stock.refresh_from_db()
    new_stock = stock.__class__.objects.create(
        receive_item=None,
        qty_in=1,
        from_stock=stock,
        container=container,
        location=stock.location,
    )
    stock.refresh_from_db()
    return new_stock
