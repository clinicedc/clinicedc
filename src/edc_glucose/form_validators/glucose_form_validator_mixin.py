from edc_constants.constants import YES

from ..utils import validate_glucose_as_millimoles_per_liter


class GlucoseFormValidatorMixin:
    def validate_glucose_test(self):
        self.required_if(YES, field="glucose_performed", field_required="glucose_date")
        self.required_if(YES, field="glucose_performed", field_required="fasting")
        self.required_if(YES, field="glucose_performed", field_required="glucose_value")
        validate_glucose_as_millimoles_per_liter("glucose", self.cleaned_data)
        self.required_if(YES, field="glucose_performed", field_required="glucose_quantifier")
        self.required_if(YES, field="glucose_performed", field_required="glucose_units")
