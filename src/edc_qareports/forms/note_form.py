from django import forms

from edc_form_validators import FormValidator, FormValidatorMixin
from edc_model_form.mixins import BaseModelFormMixin
from edc_sites.modelform_mixins import SiteModelFormMixin

from ..models import Note


class NoteFormValidator(FormValidator):
    def clean(self):
        self.required_if_true(True, field_required="note")


class NoteForm(
    SiteModelFormMixin,
    BaseModelFormMixin,
    FormValidatorMixin,
    forms.ModelForm,
):

    report_datetime_field_attr = "report_datetime"
    form_validator_cls = NoteFormValidator

    class Meta:
        model = Note
        fields = "__all__"
        help_text = {"subject_identifier": "(read-only)", "name": "(read-only)"}
        widgets = {
            "report_model": forms.TextInput(attrs={"readonly": "readonly"}),
            "subject_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
            "name": forms.TextInput(attrs={"readonly": "readonly"}),
        }
