from django import forms

from ..models import MedicationProduct


class MedicationProductForm(forms.ModelForm):
    class Meta:
        model = MedicationProduct
        fields = "__all__"
