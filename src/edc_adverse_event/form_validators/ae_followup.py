from edc_form_validators import FormValidator
from edc_reportable import SEVERITY_INCREASED_FROM_G3


class AeFollowupFormValidator(FormValidator):
    def clean(self):
        self.applicable_if(
            SEVERITY_INCREASED_FROM_G3, field="outcome", field_applicable="ae_grade"
        )
        self.applicable_if(
            SEVERITY_INCREASED_FROM_G3, field="outcome", field_applicable="ae_grade"
        )
