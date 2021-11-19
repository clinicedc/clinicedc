from django import forms

from ..models import MedicationStockReceiving


class MedicationStockReceivingForm(forms.ModelForm):
    class Meta:
        model = MedicationStockReceiving
        fields = "__all__"
