from edc_constants.constants import CLOSED, NO
from edc_form_validators import FormValidator


class AeTmgFormValidator(FormValidator):
    def clean(self):

        self.validate_other_specify(field="ae_classification")

        self.required_if(NO, field="original_report_agreed", field_required="narrative")

        self.required_if(
            CLOSED, field="report_status", field_required="report_closed_datetime"
        )
