from django import forms


class AliquotForm(forms.ModelForm):

    aliquot_identifier = forms.CharField(
        label='Aliquot identifier',
        disabled=True)

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
