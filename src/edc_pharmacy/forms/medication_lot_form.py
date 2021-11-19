from django import forms

from ..models import MedicationLot


class MedicationLotForm(forms.ModelForm):
    class Meta:
        model = MedicationLot
        fields = "__all__"
