from django.core.exceptions import ObjectDoesNotExist
from edc_appointment.utils import get_next_appointment
from edc_constants.constants import NO, YES
from edc_form_validators import INVALID_ERROR, FormValidator

from ...utils import get_rx_model_cls, get_rxrefill_model_cls


class StudyMedicationFormValidator(FormValidator):
    def clean(self):
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
            self.raise_validation_error(
                {"refill_end_datetime": "Invalid. End date must be after the start date"},
                INVALID_ERROR,
            )
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
