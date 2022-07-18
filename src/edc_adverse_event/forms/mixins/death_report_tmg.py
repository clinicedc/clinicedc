from django import forms
from edc_form_validators import FormValidatorMixin
from edc_sites.forms import SiteModelFormMixin

from ...form_validators import DeathReportTmgFormValidator


class DeathReportTmgModelFormMixin(
    SiteModelFormMixin,
    FormValidatorMixin,
):

    form_validator_cls = DeathReportTmgFormValidator

    class Meta:
        help_text = {"subject_identifier": "(read-only)", "action_identifier": "(read-only)"}
        widgets = {
            "subject_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
            "action_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
