from django import forms

from edc_base.modelform_mixins import OtherSpecifyValidationMixin


class BoxTypeForm(OtherSpecifyValidationMixin, forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('across') * cleaned_data.get('down') != cleaned_data.get('total'):
            raise forms.ValidationError('Invalid dimensions or total')
        return cleaned_data
