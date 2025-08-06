from django import forms
from edc_action_item.forms import ActionItemFormMixin
from edc_form_validators import FormValidatorMixin

from ..models import SubjectLocator
from .subject_locator_form_validator import SubjectLocatorFormValidator


class SubjectLocatorForm(FormValidatorMixin, ActionItemFormMixin, forms.ModelForm):
    form_validator_cls = SubjectLocatorFormValidator

    subject_identifier = forms.CharField(
        label="Subject Identifier",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    class Meta:
        model = SubjectLocator
        fields = "__all__"
