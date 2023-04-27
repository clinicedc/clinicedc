from edc_constants.constants import YES
from edc_form_validators import FormValidator


class AeInitialFormValidator(FormValidator):
    def clean(self):
        self.validate_other_specify(field="ae_classification")

        self.validate_relationship_to_study_drug()

        self.required_if(YES, field="ae_cause", field_required="ae_cause_other")

        self.applicable_if(YES, field="sae", field_applicable="sae_reason")

        self.applicable_if(YES, field="susar", field_applicable="susar_reported")

    def validate_relationship_to_study_drug(self):
        pass
