from django import forms
from edc_form_validators import FormValidatorMixin

from edc_adherence.model_form_mixin import MedicationAdherenceFormMixin

from .models import MedicationAdherence


class MedicationAdherenceForm(
    MedicationAdherenceFormMixin, FormValidatorMixin, forms.ModelForm
):
    class Meta:
        model = MedicationAdherence
        fields = "__all__"
