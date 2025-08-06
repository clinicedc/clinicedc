from django import forms
from edc_form_validators import FormValidatorMixin

from ..form_validators import HealthFacilityFormValidator
from ..models import HealthFacility


class HealthFacilityForm(FormValidatorMixin, forms.ModelForm):
    form_validator_cls = HealthFacilityFormValidator

    class Meta:
        model = HealthFacility
        fields = "__all__"
