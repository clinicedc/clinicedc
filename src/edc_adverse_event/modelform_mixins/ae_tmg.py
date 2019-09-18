from django import forms
from edc_action_item.forms import ActionItemFormMixin
from edc_form_validators import FormValidatorMixin
from edc_registration.modelform_mixins import ModelFormSubjectIdentifierMixin
from edc_constants.constants import CLOSED, NO
from edc_form_validators import FormValidator


class DefaultAeTmgFormValidator(FormValidator):
    def clean(self):

        self.validate_other_specify(field="ae_classification")

        self.required_if(NO, field="original_report_agreed", field_required="narrative")

        self.required_if(
            CLOSED, field="report_status", field_required="report_closed_datetime"
        )


class AeTmgModelFormMixin(
    FormValidatorMixin, ModelFormSubjectIdentifierMixin, ActionItemFormMixin
):

    form_validator_cls = DefaultAeTmgFormValidator

    subject_identifier = forms.CharField(
        label="Subject Identifier",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    ae_description = forms.CharField(
        label="Original AE Description",
        required=False,
        widget=forms.Textarea(attrs={"readonly": "readonly", "cols": "79"}),
    )

    ae_classification = forms.CharField(
        label="AE Classification",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )
