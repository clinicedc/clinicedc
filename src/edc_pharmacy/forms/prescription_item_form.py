from django import forms

from ..models import PrescriptionItem


class PrescriptionItemForm(forms.ModelForm):

    class Meta:
        model = PrescriptionItem
        fields = '__all__'
