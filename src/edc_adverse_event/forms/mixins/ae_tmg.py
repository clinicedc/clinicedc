from django import forms
from edc_constants.constants import CLOSED, NO
from edc_form_validators import FormValidator, FormValidatorMixin
from edc_registration.modelform_mixins import ModelFormSubjectIdentifierMixin


class DefaultAeTmgFormValidator(FormValidator):
    def clean(self):

        self.validate_other_specify(field="ae_classification")

        self.required_if(NO, field="original_report_agreed", field_required="narrative")

        self.required_if(
            CLOSED, field="report_status", field_required="report_closed_datetime"
        )


class AeTmgModelFormMixin(FormValidatorMixin, ModelFormSubjectIdentifierMixin):

    form_validator_cls = DefaultAeTmgFormValidator

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
            "ae_description": forms.TextInput(attrs={"readonly": "readonly", "cols": "79"}),
            "ae_classification": forms.TextInput(attrs={"readonly": "readonly"}),
            "ae_classification_other": forms.TextInput(attrs={"readonly": "readonly"}),
        }
