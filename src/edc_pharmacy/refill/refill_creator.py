from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional, Union
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from edc_utils import convert_php_dateformat

from ..exceptions import PrescriptionError, PrescriptionExpired, PrescriptionNotStarted
from ..models import Rx, RxRefill
from .refill import Refill


class RefillCreatorError(Exception):
    pass


def convert_to_utc_date(dte: Union[datetime, date]) -> date:
    try:
        dt = dte.astimezone(ZoneInfo("UTC")).date()
    except AttributeError:
        dt = dte
    return dt


class RefillCreator:
    def __init__(
        self,
        instance: Optional[models.Model] = None,
        subject_identifier: Optional[str] = None,
        visit_code: Optional[str] = None,
        visit_code_sequence: Optional[int] = None,
        refill_date: Union[datetime, date, type(None)] = None,
        formulation: Optional[Any] = None,
        number_of_days: Optional[int] = None,
        dosage_guideline: Optional[models.Model] = None,
        make_active: Optional[bool] = None,
        force_active: Optional[bool] = None,
        roundup_divisible_by: Optional[int] = None,
        weight_in_kgs: Optional[Union[float, Decimal]] = None,
        **kwargs,
    ):
        """Creates a refill.

        :type instance: model instance with other
                        attrs (visit_code, ...),
                        e.g. study medication CRF
        """
        if instance:
            visit_model_attr = getattr(instance, "visit_model_attr", None)
            if visit_model_attr:
                self.subject_identifier = getattr(
                    instance, visit_model_attr
                ).subject_identifier
                self.visit_code = getattr(instance, visit_model_attr).visit_code
                self.visit_code_sequence = getattr(
                    instance, visit_model_attr
                ).visit_code_sequence
            else:
                self.subject_identifier = instance.subject_identifier
                self.visit_code = instance.visit_code
                self.visit_code_sequence = instance.visit_code_sequence
            self.refill_date = convert_to_utc_date(instance.refill_date)
            self.formulation = instance.formulation
            self.number_of_days = instance.number_of_days
            self.dosage_guideline = instance.dosage_guideline
            self.roundup_divisible_by = instance.roundup_divisible_by
            self.weight_in_kgs = getattr(instance, "weight_in_kgs", None)

        else:
            self.subject_identifier = subject_identifier
            self.visit_code = visit_code
            self.visit_code_sequence = visit_code_sequence
            self.refill_date = convert_to_utc_date(refill_date)
            self.formulation = formulation
            self.number_of_days = number_of_days
            self.dosage_guideline = dosage_guideline
            self.roundup_divisible_by = roundup_divisible_by or 0
            self.weight_in_kgs = weight_in_kgs

        if not self.weight_in_kgs:
            self.weight_in_kgs = self._rx.weight_in_kgs
        if self.dosage_guideline.dose_per_kg and not self.weight_in_kgs:
            raise RefillCreatorError("Dosage guideline requires patient's weight in kgs")

        self.make_active = True if make_active is None else make_active
        self.force_active = force_active
        self.refill = Refill(rx_refill=self.create_or_update())
        if self.make_active:
            self.refill.activate()

    @property
    def options(self) -> dict:
        return dict(
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
            refill_date=self.refill_date,
            number_of_days=self.number_of_days,
            weight_in_kgs=self.weight_in_kgs,
            roundup_divisible_by=self.roundup_divisible_by,
        )

    def create_or_update(self) -> Any:
        """Creates / updates and returns a RxRefill."""
        get_opts = dict(
            rx=self._rx,
            visit_code=self.visit_code,
            visit_code_sequence=self.visit_code_sequence,
        )
        try:
            obj = RxRefill.objects.get(**get_opts)
        except ObjectDoesNotExist:
            obj = RxRefill.objects.create(**self.options, **get_opts)
        else:
            for k, v in self.options.items():
                setattr(obj, k, v)
            obj.save()
            obj.refresh_from_db()
        return obj

    @property
    def _rx(self) -> Any:
        """Returns Rx model instance else raises PrescriptionError"""
        opts = dict(
            subject_identifier=self.subject_identifier,
            medications__in=[self.formulation.medication],
        )
        try:
            obj = Rx.objects.get(**opts)
        except ObjectDoesNotExist:
            raise PrescriptionError(f"Subject does not have a prescription. Got {opts}.")
        else:
            refill_date = self.refill_date.strftime(
                convert_php_dateformat(settings.DATETIME_FORMAT)
            )
            if self.refill_date < obj.rx_date:
                rx_date = obj.rx_date.strftime(
                    convert_php_dateformat(settings.DATETIME_FORMAT)
                )
                raise PrescriptionNotStarted(
                    f"Subject's prescription not started. Starts on {rx_date}. "
                    f"Got {self.subject_identifier} attempting refill on {refill_date}."
                )
            elif obj.rx_expiration_date and self.refill_date > obj.rx_expiration_date:
                rx_expiration_date = obj.rx_expiration_date.strftime(
                    convert_php_dateformat(settings.DATETIME_FORMAT)
                )
                raise PrescriptionExpired(
                    f"Subject prescription has expired. Expired on {rx_expiration_date}. "
                    f"Got {self.subject_identifier} attempting refill on {refill_date}."
                )
        return obj
