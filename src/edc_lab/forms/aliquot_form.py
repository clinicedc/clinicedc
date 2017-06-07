from django import forms

from ..models import Aliquot


class AliquotForm(forms.ModelForm):

    aliquot_identifier = forms.CharField(
        label='Aliquot identifier',
        disabled=True)

    class Meta:
        model = Aliquot
        fields = '__all__'
