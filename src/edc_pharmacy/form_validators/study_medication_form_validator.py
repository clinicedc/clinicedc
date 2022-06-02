from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import NO, YES
from edc_form_validators import INVALID_ERROR, FormValidator

from ..models import Rx, RxRefill


class StudyMedicationFormValidator(FormValidator):
    def clean(self):
        self.required_if(YES, field="order_next", field_required="next_dosage_guideline")
        if self.cleaned_data.get("order_next") == NO and self.next_refill:
            if self.next_refill.active:
                self.raise_validation_error(
                    "Invalid. Next refill is already active", INVALID_ERROR
                )
        if (
            self.cleaned_data.get("order_next") == NO
            and not self.cleaned_data.get("subject_visit").appointment.next
        ):
            self.raise_validation_error(
                "Invalid. This is the last scheduled visit", INVALID_ERROR
            )

        self.required_if(YES, field="order_next", field_required="next_formulation")

    @property
    def next_refill(self):
        for obj in RxRefill.objects.filter(
            rx=self.rx,
            refill_date__gt=self.cleaned_data.get("refill_date"),
        ).order_by("refill_date"):
            return obj
        return None

    @property
    def rx(self):
        try:
            return Rx.objects.get(
                subject_identifier=self.cleaned_data.get("subject_visit").subject_identifier,
                medications__in=[self.cleaned_data.get("formulation").medication],
            )
        except ObjectDoesNotExist:
            self.raise_validation_error(
                {"__all__": "Prescription does not exist"}, INVALID_ERROR
            )
