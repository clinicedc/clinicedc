from django import forms
from edc_action_item.forms import ActionItemFormMixin
from edc_form_validators import FormValidatorMixin
from edc_model_form.mixins import BaseModelFormMixin
from edc_offstudy.modelform_mixins import OffstudyNonCrfModelFormMixin
from edc_sites.forms import SiteModelFormMixin

from ..form_validators import ProtocolDeviationViolationFormValidator
from ..models import ProtocolDeviationViolation


class ProtocolDeviationViolationForm(
    SiteModelFormMixin,
    OffstudyNonCrfModelFormMixin,
    FormValidatorMixin,
    ActionItemFormMixin,
    BaseModelFormMixin,
    forms.ModelForm,
):
    report_datetime_field_attr = "report_datetime"

    form_validator_cls = ProtocolDeviationViolationFormValidator

    subject_identifier = forms.CharField(
        label="Subject Identifier",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    class Meta:
        model = ProtocolDeviationViolation
        fields = "__all__"
