from django import forms

from ..form_validators import DeathReportTmgFormValidator
from .ae_modelform_mixin import AeModelFormMixin


class DeathReportTmgSecondModelFormMixin(AeModelFormMixin):
    form_validator_cls = DeathReportTmgFormValidator

    class Meta:
        help_text = {"subject_identifier": "(read-only)", "action_identifier": "(read-only)"}
        widgets = {
            "subject_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
            "action_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
