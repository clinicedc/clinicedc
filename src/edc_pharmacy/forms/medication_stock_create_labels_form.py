from django import forms

from ..models import MedicationStockCreateLabels


class MedicationStockCreateLabelsForm(forms.ModelForm):
    class Meta:
        model = MedicationStockCreateLabels
        fields = "__all__"
