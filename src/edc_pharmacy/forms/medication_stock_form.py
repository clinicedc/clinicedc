from django import forms

from ..models import MedicationStock


class MedicationStockForm(forms.ModelForm):
    class Meta:
        model = MedicationStock
        fields = "__all__"
