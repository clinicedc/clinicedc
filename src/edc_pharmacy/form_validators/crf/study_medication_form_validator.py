from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import NO, YES
from edc_crf.crf_form_validator import CrfFormValidator
from edc_form_validators import INVALID_ERROR
from edc_utils import formatted_datetime

from ...utils import get_rx_model_cls, get_rxrefill_model_cls

if TYPE_CHECKING:
    from edc_appointment.models import Appointment

    from ...models import Formulation, Medication, Rx, RxRefill


class StudyMedicationFormValidator(CrfFormValidator):
    def clean(self):
        next_appt_datetime = None

        self.confirm_has_rx()

        if self.related_visit.appointment.relative_next:
            next_appt_datetime = self.related_visit.appointment.relative_next.appt_datetime

        if next_appt_datetime:
            if (
                self.refill_start_datetime
                and self.refill_start_datetime.astimezone(ZoneInfo("UTC")) > next_appt_datetime
            ):
                local_dte = formatted_datetime(next_appt_datetime)
                error_msg = (
                    "Refill start date cannot be after next appointmnent date. "
                    f"Next appointment date is {local_dte}."
                )

                self.raise_validation_error(
                    {"refill_start_datetime": error_msg}, INVALID_ERROR
                )

        self.validate_refill_start_date_against_offschedule_date()

        self.required_if(
            NO,
            field="refill_to_next_visit",
            field_required="refill_end_datetime",
            inverse=False,
        )

        if not self.next_appointment and self.cleaned_data.get("refill_to_next_visit") == YES:
            error_msg = "Invalid. Subject does not have a future appointment."
            self.raise_validation_error({"refill_to_next_visit": error_msg}, INVALID_ERROR)

        self.validate_refill_dates()

        self.validate_refill_end_date_against_offschedule_date()

    def confirm_has_rx(self) -> Rx | None:
        return self.rx

    @property
    def refill_start_datetime(self) -> datetime | None:
        if refill_start_datetime := self.cleaned_data.get("refill_start_datetime"):
            return refill_start_datetime.astimezone(ZoneInfo("UTC"))
        return refill_start_datetime

    @property
    def refill_end_datetime(self) -> datetime | None:
        if refill_end_datetime := self.cleaned_data.get("refill_end_datetime"):
            return refill_end_datetime.astimezone(ZoneInfo("UTC"))
        return refill_end_datetime

    @property
    def next_refill(self) -> RxRefill | None:
        next_refill = None
        if self.refill_start_datetime:
            for obj in (
                get_rxrefill_model_cls()
                .objects.filter(
                    rx=self.rx,
                    refill_start_datetime__gt=self.refill_start_datetime,
                )
                .order_by("refill_start_datetime")
            ):
                next_refill = obj
        return next_refill

    @property
    def rx(self) -> Rx:
        try:
            return get_rx_model_cls().objects.get(
                subject_identifier=self.subject_identifier,
                medications__in=[self.medication],
            )
        except ObjectDoesNotExist:
            self.raise_validation_error(
                {"__all__": "Prescription does not exist"}, INVALID_ERROR
            )

    @property
    def formulation(self) -> Formulation | None:
        return self.cleaned_data.get("formulation")

    @property
    def medication(self) -> Medication:
        if self.formulation:
            return self.formulation.medication
        else:
            self.raise_validation_error(
                {"__all__": "Need the formulation to look up the prescription."}, INVALID_ERROR
            )

    @property
    def next_appointment(self) -> Appointment | None:
        return self.related_visit.appointment.next

    def validate_refill_start_date_against_offschedule_date(self):
        if (
            self.offschedule_datetime
            and self.refill_start_datetime
            and self.refill_start_datetime > self.offschedule_datetime
        ):
            error_msg = (
                "Invalid. Cannot be after offschedule datetime. "
                f"Got {self.offschedule_datetime}."
            )
            self.raise_validation_error({"refill_start_datetime": error_msg}, INVALID_ERROR)

    def validate_refill_end_date_against_offschedule_date(self):
        if (
            self.offschedule_datetime
            and self.refill_end_datetime
            and self.refill_end_datetime > self.offschedule_datetime
        ):
            error_msg = (
                "Invalid. Cannot be after offschedule datetime. "
                f"Got {self.offschedule_datetime}."
            )
            self.raise_validation_error({"refill_end_datetime": error_msg}, INVALID_ERROR)

    def validate_refill_dates(self):
        if (
            self.refill_start_datetime
            and self.cleaned_data.get("refill")
            and self.cleaned_data.get("refill") == NO
        ):
            error_msg = (
                "Subject is not receiving study medication. Refill end date "
                "and time must exactly match refill start date and time."
            )
            if not self.refill_end_datetime:
                self.raise_validation_error({"refill_end_datetime": error_msg}, INVALID_ERROR)
            elif self.refill_start_datetime != self.refill_end_datetime:
                self.raise_validation_error({"refill_end_datetime": error_msg}, INVALID_ERROR)

        if (
            self.cleaned_data.get("refill")
            and self.refill_start_datetime
            and self.refill_end_datetime
            and self.cleaned_data.get("refill") == YES
            and self.refill_start_datetime >= self.refill_end_datetime
        ):
            if self.cleaned_data.get("refill_to_next_visit") == YES:
                error_msg = (
                    "Invalid. The calculated refill end date will be before "
                    f"the start date! Got {self.cleaned_data.get('refill_end_datetime')}. "
                    "Check the refill start date."
                )
            else:
                error_msg = (
                    "Invalid. Refill end date must be after the refill start date and "
                    "before the next visit"
                )
            self.raise_validation_error({"refill_end_datetime": error_msg}, INVALID_ERROR)
