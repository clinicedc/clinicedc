from django import forms
from edc_action_item.forms.action_item_form_mixin import ActionItemFormMixin
from edc_form_validators.form_validator import FormValidator
from edc_form_validators.form_validator_mixins import FormValidatorMixin
from edc_sites.forms import SiteModelFormMixin

from ..models import UnblindingRequest


class UnblindingRequestFormValidator(FormValidator):
    pass


class UnblindingRequestForm(
    SiteModelFormMixin, FormValidatorMixin, ActionItemFormMixin, forms.ModelForm
):
    form_validator_cls = UnblindingRequestFormValidator

    subject_identifier = forms.CharField(
        label="Subject Identifier",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    class Meta:
        model = UnblindingRequest
        fields = "__all__"
