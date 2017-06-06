from django import forms

from edc_base.modelform_mixins import OtherSpecifyValidationMixin

from ..models import Manifest


class ManifestForm(OtherSpecifyValidationMixin, forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        self.validate_other_specify('category')
        return cleaned_data

    class Meta:
        fields = '__all__'
        model = Manifest
