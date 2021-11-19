from django import forms

from ..models import MedicationOrder


class MedicationOrderForm(forms.ModelForm):
    class Meta:
        model = MedicationOrder
        fields = "__all__"
