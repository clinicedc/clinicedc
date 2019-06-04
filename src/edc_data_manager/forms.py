from django import forms
from edc_form_validators.form_validator_mixin import FormValidatorMixin
from edc_action_item.forms.action_item_form_mixin import ActionItemFormMixin

from .models import DataManagerQuery, Query


class DataManagerQueryForm(FormValidatorMixin, ActionItemFormMixin, forms.ModelForm):
    class Meta:
        model = DataManagerQuery
        fields = "__all__"


class QueryForm(FormValidatorMixin, forms.ModelForm):
    class Meta:
        model = Query
        fields = "__all__"
