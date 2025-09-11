from clinicedc_tests.models import MedicationAdherence
from django import forms

from edc_adherence.form_validator_mixin import MedicationAdherenceFormValidatorMixin
from edc_adherence.model_form_mixin import MedicationAdherenceFormMixin
from edc_form_validators import FormValidator, FormValidatorMixin


class MedicationAdherenceFormValidator(MedicationAdherenceFormValidatorMixin, FormValidator):
    pass


class MedicationAdherenceForm(
    MedicationAdherenceFormMixin, FormValidatorMixin, forms.ModelForm
):
    form_validator_cls = MedicationAdherenceFormValidator

    class Meta:
        model = MedicationAdherence
        fields = "__all__"
