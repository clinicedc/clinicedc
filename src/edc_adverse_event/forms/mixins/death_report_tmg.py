from django import forms
from edc_action_item.forms import ActionItemFormMixin
from edc_form_validators import FormValidatorMixin
from edc_sites.forms import SiteModelFormMixin

from ...form_validators import DeathReportTmgFormValidator


class DeathReportTmgModelFormMixin(
    SiteModelFormMixin,
    ActionItemFormMixin,
    FormValidatorMixin,
):

    form_validator_cls = DeathReportTmgFormValidator

    subject_identifier = forms.CharField(
        label="Subject identifier",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )
