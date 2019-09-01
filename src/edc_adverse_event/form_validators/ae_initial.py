from edc_form_validators import FormValidator
from edc_constants.constants import YES


class AeInitialFormValidator(FormValidator):
    def clean(self):

        self.required_if(YES, field="ae_cause", field_required="ae_cause_other")

        self.applicable_if(YES, field="sae", field_applicable="sae_reason")
