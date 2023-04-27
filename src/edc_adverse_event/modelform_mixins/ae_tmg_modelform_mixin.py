from django import forms

from ..form_validators import AeTmgFormValidator
from .ae_modelform_mixin import AeModelFormMixin


class AeTmgModelFormMixin(AeModelFormMixin):
    form_validator_cls = AeTmgFormValidator

    class Meta:
        labels = {
            "ae_description": "Original AE Description",
            "ae_classification": "AE Classification",
            "ae_classification_other": "AE Classification (if `other` above)",
        }
        help_text = {
            "subject_identifier": "(read-only)",
            "action_identifier": "(read-only)",
            "ae_description": "(read-only)",
            "ae_classification": "(read-only)",
            "ae_classification_other": "(read-only)",
        }
        widgets = {
            "subject_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
            "action_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
            "ae_description": forms.Textarea(attrs={"readonly": "readonly", "cols": "79"}),
            "ae_classification": forms.TextInput(attrs={"readonly": "readonly"}),
            "ae_classification_other": forms.TextInput(attrs={"readonly": "readonly"}),
        }
