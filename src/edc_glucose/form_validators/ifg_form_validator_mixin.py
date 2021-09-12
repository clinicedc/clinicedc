from edc_constants.constants import YES
from edc_form_validators import FormValidator


class IfgFormValidatorMixin(FormValidator):
    def validate_ifg_required_fields(self):
        """Uses fields `fasting`,`fasting_duration_str`, `ifg_value`,
        `ifg_datetime`, `ifg_units`
        """
        self.required_if(YES, field="fasting", field_required="fasting_duration_str")

        self.required_if(YES, field="fasting", field_required="ifg_datetime")

        self.required_if(YES, field="fasting", field_required="ifg_value")

        self.required_if_true(
            self.cleaned_data.get("ifg_datetime"),
            field_required="ifg_value",
        )

        self.required_if_true(
            self.cleaned_data.get("ifg_value"),
            field_required="ifg_units",
        )

        self.required_if_true(
            self.cleaned_data.get("ifg_value"),
            field_required="ifg_datetime",
        )
