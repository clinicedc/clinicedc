from clinicedc_constants import AE_WITHDRAWN, SEVERITY_INCREASED_FROM_G3, YES

from edc_form_validators import INVALID_ERROR, FormValidator


class AeFollowupFormValidator(FormValidator):
    def clean(self):
        self.applicable_if(
            SEVERITY_INCREASED_FROM_G3, field="outcome", field_applicable="ae_grade"
        )
        self.applicable_if(
            SEVERITY_INCREASED_FROM_G3, field="outcome", field_applicable="ae_grade"
        )
        if (
            self.cleaned_data.get("outcome")
            and self.cleaned_data.get("followup")
            and self.cleaned_data.get("outcome") == AE_WITHDRAWN
            and self.cleaned_data.get("followup") == YES
        ):
            self.raise_validation_error(
                {"followup": "AE was reported as withrawn. Expected NO"}, INVALID_ERROR
            )
