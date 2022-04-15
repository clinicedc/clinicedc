from datetime import date, datetime
from typing import Any, Optional, Union

import arrow
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, models, transaction
from edc_utils import convert_php_dateformat

from ..exceptions import (
    PrescriptionError,
    PrescriptionExpired,
    PrescriptionNotStarted,
    RefillAlreadyExists,
)
from ..models import Rx, RxRefill
from .refill import Refill


def convert_to_utc_date(dte: Union[datetime, date]) -> date:
    try:
        dt = dte.date()
    except AttributeError:
        dt = arrow.get(dte).to("utc").date()
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
        **kwargs,
    ):
        """Creates a refill.

        :type instance: model instance with other
                        attrs (visit_code, ...),
                        e.g. study medication CRF
        """
        super().__init__(**kwargs)
        if instance:
            self.subject_identifier = instance.get_subject_identifier()
            self.visit_code = instance.visit_code
            self.visit_code_sequence = instance.visit_code_sequence
            self.refill_date = convert_to_utc_date(instance.refill_date)
            self.formulation = instance.formulation
            self.number_of_days = instance.number_of_days
            self.dosage_guideline = instance.dosage_guideline

        else:
            self.subject_identifier = subject_identifier
            self.visit_code = visit_code
            self.visit_code_sequence = visit_code_sequence
            self.refill_date = convert_to_utc_date(refill_date)
            self.formulation = formulation
            self.number_of_days = number_of_days
            self.dosage_guideline = dosage_guideline
        self.make_active = True if make_active is None else make_active
        self.force_active = force_active
        self.refill = Refill(self.create())
        if self.make_active:
            self.refill.activate()

    def create(self) -> Any:
        get_opts = dict(
            rx=self._rx,
            visit_code=self.visit_code,
            visit_code_sequence=self.visit_code_sequence,
        )
        create_opts = dict(
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
            refill_date=self.refill_date,
            number_of_days=self.number_of_days,
            **get_opts,
        )
        try:
            obj = RxRefill.objects.get(**get_opts)
        except ObjectDoesNotExist:
            try:
                with transaction.atomic():
                    obj = RxRefill.objects.create(**create_opts)
            except IntegrityError as e:
                raise RefillAlreadyExists(f"Refill already exists. {e}. See {obj}.")
        else:
            raise RefillAlreadyExists(f"Refill already exists. Got {obj}.")
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
            raise PrescriptionError(
                f"Subject does not have a prescription. Got {opts}."
            )
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
