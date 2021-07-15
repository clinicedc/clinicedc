from edc_constants.constants import YES
from edc_form_validators import FormValidator

from .ltfu_form_validator_mixin import LtfuFormValidatorMixin


class LtfuFormValidator(LtfuFormValidatorMixin, FormValidator):
    def clean(self):
        self.validate_ltfu()
        self.required_if(YES, field="home_visit", field_required="home_visit_detail")
        self.validate_other_specify(
            field="loss_category", other_specify_field="loss_category_other"
        )
