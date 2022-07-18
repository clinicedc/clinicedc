from django import forms
from edc_form_validators import FormValidator, FormValidatorMixin
from edc_registration.modelform_mixins import ModelFormSubjectIdentifierMixin


class DefaultAeSusarFormValidator(FormValidator):
    pass


class AeSusarModelFormMixin(FormValidatorMixin, ModelFormSubjectIdentifierMixin):

    form_validator_cls = DefaultAeSusarFormValidator

    class Meta:
        help_text = {"subject_identifier": "(read-only)", "action_identifier": "(read-only)"}
        widgets = {
            "subject_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
            "action_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
