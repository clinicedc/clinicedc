from __future__ import annotations

import base64
import string
from binascii import Error
from decimal import Decimal
from typing import TYPE_CHECKING

from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from edc_registration.models import RegisteredSubject
from edc_visit_tracking.utils import get_previous_related_visit

from .exceptions import (
    ChecksumError,
    InsufficientStockError,
    ProcessStockRequestError,
    RepackageError,
    StockError,
)

if TYPE_CHECKING:
    from .models import Container, Location, Request, RequestItem, Stock


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


def repackage_stock(
    stock: Stock,
    container: Container,
    from_location: Location | None = None,
    to_location: Location | None = None,
    request_item: RequestItem | None = None,
) -> Stock:
    """Take from stock and fill container as new stock item"""
    # location may only change for requests
    if to_location and stock.location != from_location:
        raise RepackageError(
            f"Stock location error. Expected stock to be from {from_location}"
        )
    if (
        to_location
        and from_location
        and to_location != from_location
        and not container.may_request_as
    ):
        raise RepackageError(
            "Invalid container. Container may not be used if location changes. "
            "Is this for a stock request?"
        )
    if stock.unit_qty_in - stock.unit_qty_out == Decimal(0):
        raise InsufficientStockError()
    if stock.unit_qty_in - stock.unit_qty_out < 0:
        raise StockError("Unit qty in cannot be less than unit qty out")
    new_stock = stock.__class__.objects.create(
        receive_item=None,
        qty_in=1,
        from_stock=stock,
        container=container,
        location=to_location or stock.location,
        request_item=request_item,
    )
    stock.refresh_from_db()
    return new_stock


def process_request(request: Request, source_location: Location, source_container: Container):

    # TODO: look at available local stock first before checking central stock

    qs = (
        RegisteredSubject.objects.values("randomization_list_model")
        .filter(randomization_list_model__isnull=False)
        .annotate(model_name=Count("randomization_list_model"))
    )
    if qs.count() > 1:
        raise ProcessStockRequestError("More than one randomization_list_model found.")
    model_cls = django_apps.get_model(qs.filter()[0]["randomization_list_model"])
    for request_item in django_apps.get_model("edc_pharmacy.requestitem").objects.filter(
        request=request
    ):

        rando = model_cls.objects.get(subject_identifier=request_item.subject_identifier)
        request_item.sid = rando.sid
        request_item.site = rando.allocated_site
        request_item.gender = RegisteredSubject.objects.get(
            subject_identifier=request_item.subject_identifier
        ).gender
        request_item.save()

        assignment = django_apps.get_model("edc_pharmacy.assignment").objects.get(
            name=rando.assignment
        )

        stock = django_apps.get_model("edc_pharmacy.stock").objects.in_stock(
            unit_qty=request_item.request.container.qty,
            container=source_container,
            assignment=assignment,
            location=source_location,
        )
        if stock:
            repackage_stock(
                stock,
                request_item.request.container,
                from_location=source_location,
                to_location=request_item.request.location,
                request_item=request_item,
            )


def generate_code_with_checksum_from_id(id_number: int) -> str:
    bytes_id = id_number.to_bytes((id_number.bit_length() + 7) // 8, "big")
    code = base64.b32encode(bytes_id).decode("utf-8")
    code = code.rstrip("=")
    checksum = sum(ord(c) * (i + 1) for i, c in enumerate(code)) % 36
    checksum_char = (
        string.digits[checksum] if checksum < 10 else string.ascii_uppercase[checksum - 10]
    )
    return code + checksum_char


def decode_code_with_checksum(code: str) -> int:
    if code != add_checksum(code[:-1]):
        raise ChecksumError(f"Invalid checksum for code. Got {code}")
    padding_length = (8 - (len(code[:-1]) % 8)) % 8
    padded_code = code[:-1] + ("=" * padding_length)
    try:
        decoded_bytes = base64.b32decode(padded_code)
    except Error as e:
        raise ValueError(f"Failed to decode string: {str(e)}")
    return int.from_bytes(decoded_bytes, "big")


def add_checksum(code):
    checksum = sum(ord(c) * (i + 1) for i, c in enumerate(code)) % 36
    checksum_char = (
        string.digits[checksum] if checksum < 10 else string.ascii_uppercase[checksum - 10]
    )
    return code + checksum_char
