from django import forms
from edc_crf.modelform_mixins import CrfModelFormMixin

from edc_pharmacy.form_validators import (
    StudyMedicationFormValidator as BaseStudyMedicationFormValidator,
)

from .models import StudyMedication


class StudyMedicationFormValidator(BaseStudyMedicationFormValidator):
    def validate_demographics(self) -> None:
        pass


class StudyMedicationForm(CrfModelFormMixin, forms.ModelForm):
    form_validator_cls = StudyMedicationFormValidator

    def validate_against_consent(self):
        pass

    class Meta:
        model = StudyMedication
        fields = "__all__"
