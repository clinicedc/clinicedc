from django import forms

from edc_base.modelform_mixins import OtherSpecifyValidationMixin


class ManifestItemForm(OtherSpecifyValidationMixin, forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
