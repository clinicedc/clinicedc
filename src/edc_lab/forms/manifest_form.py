from django import forms
from edc_form_validators import FormValidator

from ..models import Manifest


class ManifestForm(forms.ModelForm):
    def clean(self) -> dict:
        cleaned_data = super().clean()
        form_validator = FormValidator(cleaned_data=cleaned_data)
        form_validator.validate_other_specify("category")
        return cleaned_data

    class Meta:
        fields = "__all__"
        model = Manifest
