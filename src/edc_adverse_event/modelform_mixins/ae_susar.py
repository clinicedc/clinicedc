from django import forms
from edc_action_item.forms import ActionItemFormMixin
from edc_form_validators import FormValidator, FormValidatorMixin
from edc_registration.modelform_mixins import ModelFormSubjectIdentifierMixin


class DefaultAeSusarFormValidator(FormValidator):
    pass


class AeSusarModelFormMixin(
    FormValidatorMixin, ModelFormSubjectIdentifierMixin, ActionItemFormMixin
):

    form_validator_cls = DefaultAeSusarFormValidator

    subject_identifier = forms.CharField(
        label="Subject Identifier",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
        help_text="(read-only)",
    )
