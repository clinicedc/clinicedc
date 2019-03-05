from django import forms

from ..models import DosageGuideline


class DosageGuidelineForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("dose") and cleaned_data.get("dose_per_kg"):
            raise forms.ValidationError("Specify either dose or dose per kg, not both")
        if not cleaned_data.get("dose") and not cleaned_data.get("dose_per_kg"):
            raise forms.ValidationError("Either dose or dose per kg is required.")
        return cleaned_data

    class Meta:
        model = DosageGuideline
        fields = "__all__"
