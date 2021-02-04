from django import forms
from edc_form_validators import FormValidator, FormValidatorMixin

from ..models import QueryRule


class QueryRuleFormValidator(FormValidator):
    def clean(self):
        models = list(set([obj.model for obj in self.cleaned_data.get("data_dictionaries")]))
        if len(models) > 1:
            raise forms.ValidationError(
                {"data_dictionaries": "Invalid. Select questions from one CRF only"}
            )


class QueryRuleForm(FormValidatorMixin, forms.ModelForm):
    form_validator_cls = QueryRuleFormValidator

    class Meta:
        model = QueryRule
        fields = "__all__"
