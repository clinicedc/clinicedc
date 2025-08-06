from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import uuid4
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from edc_utils import convert_php_dateformat

from ..exceptions import (
    PrescriptionError,
    PrescriptionExpired,
    PrescriptionNotStarted,
    RefillCreatorError,
)
from ..utils import get_rx_model_cls, get_rxrefill_model_cls
from .activate_refill import activate_refill

if TYPE_CHECKING:
    from ..models import DosageGuideline, Formulation, Rx, RxRefill


class RefillCreator:
    def __init__(
        self,
        refill_identifier: str = None,
        subject_identifier: str = None,
        refill_start_datetime: datetime = None,
        refill_end_datetime: datetime = None,
        formulation: Formulation = None,
        dosage_guideline: DosageGuideline = None,
        make_active: bool | None = None,
        force_active: bool | None = None,
        roundup_divisible_by: int | None = None,
        weight_in_kgs: float | Decimal | None = None,
    ):
        """Creates rx_refill"""
        self._next_rx_refill = None
        self._prev_rx_refill = None
        self.refill_identifier = refill_identifier
        self.refill_end_datetime = refill_end_datetime.astimezone(ZoneInfo("UTC"))
        self.subject_identifier = subject_identifier
        self.refill_start_datetime = refill_start_datetime.astimezone(ZoneInfo("UTC"))
        self.formulation = formulation
        self.dosage_guideline = dosage_guideline
        self.roundup_divisible_by = roundup_divisible_by or 0
        self.weight_in_kgs = weight_in_kgs

        if not self.formulation:
            raise RefillCreatorError(
                f"Formulation cannot be None. Refill identifier is {refill_identifier}. "
                f"See {self.subject_identifier}."
            )
        if not self.dosage_guideline:
            raise RefillCreatorError(
                f"Dosage guideline cannot be None. Refill identifier is {refill_identifier}. "
                f"See {self.subject_identifier}."
            )
        if not self.weight_in_kgs:
            self.weight_in_kgs = self.rx.weight_in_kgs
        if self.dosage_guideline.dose_per_kg and not self.weight_in_kgs:
            raise RefillCreatorError(
                "Dosage guideline requires patient's weight in kgs. "
                f"See {self.subject_identifier}."
            )

        self.make_active = True if make_active is None else make_active
        self.force_active = force_active
        self.rx_refill = self.create_or_update()
        if self.make_active:
            activate_refill(self.rx_refill)

    def create_or_update(self) -> RxRefill:
        """Creates / updates and returns a RxRefill."""
        # find first refill on or after this start date
        opts = dict(
            refill_identifier=self.refill_identifier or uuid4(),
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
            refill_start_datetime=self.refill_start_datetime,
            refill_end_datetime=self.refill_end_datetime,
            weight_in_kgs=self.weight_in_kgs,
            roundup_divisible_by=self.roundup_divisible_by,
        )
        try:
            rx_refill = get_rxrefill_model_cls().objects.get(
                rx=self.rx, refill_start_datetime=self.refill_start_datetime
            )
        except ObjectDoesNotExist:
            if self.prev_rx_refill:
                # found previous rx_refill, update end datetime, number_of_days
                self.prev_rx_refill.refill_end_datetime = (
                    self.refill_start_datetime - relativedelta(minutes=1)
                )
                self.prev_rx_refill.save()
            if self.next_rx_refill:
                refill_end_datetime = (
                    self.next_rx_refill.refill_start_datetime - relativedelta(minutes=1)
                )
                opts.update(refill_end_datetime=refill_end_datetime)
            # create a new rx_refill
            rx_refill = get_rxrefill_model_cls().objects.create(rx=self.rx, **opts)
        else:
            refill_end_datetime = self.refill_end_datetime
            if self.next_rx_refill:
                refill_end_datetime = (
                    self.next_rx_refill.refill_start_datetime - relativedelta(minutes=1)
                )
            opts.update(refill_end_datetime=refill_end_datetime)
            for k, v in opts.items():
                setattr(rx_refill, k, v)
            rx_refill.save()
            rx_refill.refresh_from_db()
        return rx_refill

    @property
    def rx(self) -> Rx:
        """Returns Rx model instance else raises PrescriptionError"""
        opts = dict(
            subject_identifier=self.subject_identifier,
            medications__in=[self.formulation.medication],
        )
        try:
            rx = get_rx_model_cls().objects.get(**opts)
        except ObjectDoesNotExist:
            raise PrescriptionError(f"Subject does not have a prescription. Got {opts}.")
        else:
            if self.refill_start_datetime.date() < rx.rx_date:
                rx_date = rx.rx_date.strftime(convert_php_dateformat(settings.DATE_FORMAT))
                raise PrescriptionNotStarted(
                    f"Subject's prescription not started. Starts on {rx_date}. "
                    f"Got {self.subject_identifier} attempting "
                    f"refill on {self.refill_start_datetime_as_str}."
                )
            elif (
                rx.rx_expiration_date
                and self.refill_start_datetime.date() > rx.rx_expiration_date
            ):
                rx_expiration_date = rx.rx_expiration_date.strftime(
                    convert_php_dateformat(settings.DATE_FORMAT)
                )
                raise PrescriptionExpired(
                    f"Subject prescription has expired. Expired on {rx_expiration_date}. "
                    f"Got {self.subject_identifier} attempting refill "
                    f"on {self.refill_start_datetime_as_str}."
                )
        return rx

    @property
    def prev_rx_refill(self):
        if not self._prev_rx_refill:
            self._prev_rx_refill = (
                get_rxrefill_model_cls()
                .objects.filter(
                    rx=self.rx, refill_start_datetime__lt=self.refill_start_datetime
                )
                .order_by("refill_start_datetime")
                .first()
            )
        return self._prev_rx_refill

    @property
    def next_rx_refill(self):
        if not self._next_rx_refill:
            self._next_rx_refill = (
                get_rxrefill_model_cls()
                .objects.filter(
                    rx=self.rx, refill_start_datetime__gt=self.refill_start_datetime
                )
                .order_by("refill_start_datetime")
                .first()
            )
        return self._next_rx_refill

    @property
    def refill_start_datetime_as_str(self) -> str:
        return self.refill_start_datetime.strftime(
            convert_php_dateformat(settings.DATETIME_FORMAT)
        )
