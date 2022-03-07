from datetime import date, datetime
from typing import Any, Optional, Union

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction

from ..exceptions import PrescriptionError, PrescriptionRefillError
from ..models import Rx, RxRefill
from ..utils import convert_to_utc_date


class RefillCreator:
    def __init__(
        self,
        subject_identifier: Optional[str] = None,
        refill_date: Union[datetime, date, type(None)] = None,
        visit_code: Optional[str] = None,
        visit_code_sequence: Optional[int] = None,
        number_of_days: Optional[int] = None,
        dosage_guideline: Optional[Any] = None,
        formulation: Optional[Any] = None,
        instance: Optional[Any] = None,
        make_active: Optional[bool] = None,
    ):
        if instance:
            self.subject_identifier = instance.get_subject_identifier()
            self.refill_date = convert_to_utc_date(instance.refill_date)
            self.visit_code = instance.visit_code
            self.visit_code_sequence = instance.visit_code_sequence
            self.number_of_days = instance.number_of_days
            self.dosage_guideline = instance.dosage_guideline
            self.formulation = instance.formulation

        else:
            self.subject_identifier = subject_identifier
            self.refill_date = convert_to_utc_date(refill_date)
            self.visit_code = visit_code
            self.visit_code_sequence = visit_code_sequence
            self.number_of_days = number_of_days
            self.dosage_guideline = dosage_guideline
            self.formulation = formulation
        self.make_active = True if make_active is None else make_active
        self.object = self.create()

    def create(self) -> Any:
        active = False
        if self.make_active:
            if self.active_refill:
                obj = self.active_refill
                obj.active = False
                obj.save()
            active = True
        get_opts = dict(
            rx=self.rx,
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
            refill_date=self.refill_date,
        )
        create_opts = dict(
            visit_code=self.visit_code,
            visit_code_sequence=self.visit_code_sequence,
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
                raise PrescriptionRefillError(e)
        else:
            obj.visit_code = self.visit_code
            obj.visit_code_sequence = self.visit_code_sequence
            obj.number_of_days = self.number_of_days
        finally:
            obj.active = active
            obj.save()
        return obj

    @property
    def rx(self) -> Any:
        """Returns Rx model instance else raises PrescriptionError"""
        opts = dict(
            subject_identifier=self.subject_identifier,
            medication=self.formulation.medication,
            rx_date__lte=self.refill_date,
        )
        try:
            obj = Rx.objects.get(**opts)
        except ObjectDoesNotExist:
            raise PrescriptionError(
                f"Subject does not have a valid prescription. Got {opts}."
            )
        else:
            if obj.rx_expiration_date and self.refill_date > obj.rx_expiration_date:
                raise PrescriptionError(
                    f"Subject prescription has expired. Got {self.subject_identifier} on {obj.rx_expiration_date}."
                )
        return obj

    @property
    def active_refill(self) -> Any:
        """Returns the 'active' RxRefill model instance or None"""
        try:
            obj = RxRefill.objects.get(rx=self.rx, active=True)
        except ObjectDoesNotExist:
            obj = None
        return obj
