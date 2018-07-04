from django import forms

from..models import BoxType


class BoxTypeForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('across') and cleaned_data.get('down'):
            if (cleaned_data.get('across') * cleaned_data.get('down')
                    != cleaned_data.get('total')):
                raise forms.ValidationError(
                    {'total': 'Invalid total for given dimensions'})
        return cleaned_data

    class Meta:
        fields = '__all__'
        model = BoxType
