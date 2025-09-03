from django import forms

from edc_form_validators import FormValidatorMixin
from edc_model_form.mixins import BaseModelFormMixin
from edc_offstudy.modelform_mixins import OffstudyNonCrfModelFormMixin
from edc_sites.modelform_mixins import SiteModelFormMixin

from .form_validators import SubjectTransferFormValidator
from .models import SubjectTransfer


class SubjectTransferForm(
    SiteModelFormMixin,
    OffstudyNonCrfModelFormMixin,
    BaseModelFormMixin,
    FormValidatorMixin,
    forms.ModelForm,
):
    form_validator_cls = SubjectTransferFormValidator

    subject_identifier = forms.CharField(
        label="Subject Identifier",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    class Meta:
        model = SubjectTransfer
        fields = "__all__"
