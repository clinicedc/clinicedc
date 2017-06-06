from django import forms


class AliquotForm(forms.ModelForm):

    aliquot_identifier = forms.CharField(
        label='Aliquot identifier',
        disabled=True)
