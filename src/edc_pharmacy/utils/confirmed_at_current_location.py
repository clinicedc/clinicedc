from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.db.models import F

if TYPE_CHECKING:
    from edc_pharmacy.models import Stock


def confirmed_at_current_location(code) -> Stock | None:
    """Returns the stock instance if the location is current.

    To truly be the current location, the stock item must be
    confirmed at the location.
    """
    stock_model_cls: type[Stock] = django_apps.get_model("edc_pharmacy.stock")
    with contextlib.suppress(stock_model_cls.DoesNotExist):
        return stock_model_cls.objects.get(
            code=code,
            container__may_dispense_as=True,
            confirmed__isnull=False,
            allocation__isnull=False,
            stocktransferitem__isnull=False,
            location=F("stocktransferitem__stock_transfer__to_location"),
            stocktransferitem__confirmationatlocationitem__isnull=False,
        )
    return None


def is_in_transit(code):
    stock_model_cls: type[Stock] = django_apps.get_model("edc_pharmacy.stock")
    return stock_model_cls.objects.filter(
        code=code,
        container__may_dispense_as=True,
        confirmed__isnull=False,
        allocation__isnull=False,
        stocktransferitem__isnull=False,
        location=F("stocktransferitem__stock_transfer__to_location"),
        stocktransferitem__confirmationatlocationitem__isnull=True,
        dispenseitem__isnull=True,
    ).exists()


def is_at_location(code):
    stock_model_cls: type[Stock] = django_apps.get_model("edc_pharmacy.stock")
    return stock_model_cls.objects.filter(
        code=code,
        container__may_dispense_as=True,
        confirmed__isnull=False,
        allocation__isnull=False,
        stocktransferitem__isnull=False,
        location=F("stocktransferitem__stock_transfer__to_location"),
        stocktransferitem__confirmationatlocationitem__isnull=False,
        dispenseitem__isnull=True,
    ).exists()


def is_stored_at_location(code):
    stock_model_cls: type[Stock] = django_apps.get_model("edc_pharmacy.stock")
    return stock_model_cls.objects.filter(
        code=code,
        container__may_dispense_as=True,
        confirmed__isnull=False,
        allocation__isnull=False,
        stocktransferitem__isnull=False,
        location=F("stocktransferitem__stock_transfer__to_location"),
        stocktransferitem__confirmationatlocationitem__isnull=False,
        storagebinitem__isnull=False,
        dispenseitem__isnull=True,
    ).exists()


def is_dispensed(code):
    stock_model_cls: type[Stock] = django_apps.get_model("edc_pharmacy.stock")
    return stock_model_cls.objects.filter(
        code=code,
        container__may_dispense_as=True,
        confirmed__isnull=False,
        allocation__isnull=False,
        stocktransferitem__isnull=False,
        location=F("stocktransferitem__stock_transfer__to_location"),
        stocktransferitem__confirmationatlocationitem__isnull=False,
        # storagebinitem__isnull=False,
        dispenseitem__isnull=False,
    ).exists()
