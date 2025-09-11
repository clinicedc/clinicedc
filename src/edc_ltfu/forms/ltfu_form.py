from django import forms

from edc_action_item.forms.action_item_form_mixin import ActionItemFormMixin
from edc_form_validators.form_validator_mixins import FormValidatorMixin
from edc_sites.forms import SiteModelFormMixin

from ..models import Ltfu
from .ltfu_form_validator import LtfuFormValidator


class LtfuForm(SiteModelFormMixin, FormValidatorMixin, ActionItemFormMixin, forms.ModelForm):
    form_validator_cls = LtfuFormValidator

    subject_identifier = forms.CharField(
        label="Subject Identifier",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    class Meta:
        model = Ltfu
        fields = "__all__"
