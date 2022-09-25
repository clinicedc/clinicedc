from zoneinfo import ZoneInfo

from django.core.exceptions import ObjectDoesNotExist
from edc_appointment.utils import get_next_appointment
from edc_constants.constants import NO, YES
from edc_crf.crf_form_validator import CrfFormValidator
from edc_form_validators import INVALID_ERROR
from edc_utils import formatted_datetime

from ...utils import get_rx_model_cls, get_rxrefill_model_cls


class StudyMedicationFormValidator(CrfFormValidator):
    def clean(self):
        next_appt_datetime = None
        subject_visit = self.cleaned_data.get("subject_visit")
        if subject_visit.appointment.relative_next:
            next_appt_datetime = subject_visit.appointment.relative_next.appt_datetime
        if next_appt_datetime:
            if (
                self.cleaned_data.get("refill_start_datetime")
                and self.cleaned_data.get("refill_start_datetime").astimezone(ZoneInfo("UTC"))
                > next_appt_datetime
            ):
                local_dte = formatted_datetime(next_appt_datetime)
                error_msg = (
                    "Refill start date cannot be after next appointmnent date. "
                    f"Next appointment date is {local_dte}."
                )

                self.raise_validation_error(
                    {"refill_start_datetime": error_msg}, INVALID_ERROR
                )
        self.required_if(
            NO,
            field="refill_to_next_visit",
            field_required="refill_end_datetime",
            inverse=False,
        )
        if (
            self.cleaned_data.get("refill_start_datetime")
            and self.cleaned_data.get("refill_end_datetime")
            and self.cleaned_data.get("refill_start_datetime")
            >= self.cleaned_data.get("refill_end_datetime")
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
        self.required_if(
            YES, field="order_or_update_next", field_required="next_dosage_guideline"
        )
        if self.cleaned_data.get("order_or_update_next") == NO and self.next_refill:
            if self.next_refill.active:
                self.raise_validation_error(
                    "Invalid. Next refill is already active", INVALID_ERROR
                )
        if self.cleaned_data.get("order_or_update_next") == NO and not get_next_appointment(
            self.cleaned_data.get("subject_visit").appointment, include_interim=True
        ):
            self.raise_validation_error(
                "Invalid. This is the last scheduled visit", INVALID_ERROR
            )

        self.required_if(YES, field="order_or_update_next", field_required="next_formulation")

    @property
    def next_refill(self):
        for obj in (
            get_rxrefill_model_cls()
            .objects.filter(
                rx=self.rx,
                refill_start_datetime__gt=self.cleaned_data.get("refill_start_datetime"),
            )
            .order_by("refill_start_datetime")
        ):
            return obj
        return None

    @property
    def rx(self):
        try:
            return get_rx_model_cls().objects.get(
                subject_identifier=self.cleaned_data.get("subject_visit").subject_identifier,
                medications__in=[self.cleaned_data.get("formulation").medication],
            )
        except ObjectDoesNotExist:
            self.raise_validation_error(
                {"__all__": "Prescription does not exist"}, INVALID_ERROR
            )
