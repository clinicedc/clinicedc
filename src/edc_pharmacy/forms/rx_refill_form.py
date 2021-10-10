from django import forms

from ..models import RxRefill


class RxRefillForm(forms.ModelForm):
    class Meta:
        model = RxRefill
        fields = "__all__"
        # labels = {
        #     "dosage_guideline": "Medication",
        # }
