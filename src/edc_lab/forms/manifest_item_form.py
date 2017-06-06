from django import forms

from edc_base.modelform_mixins import OtherSpecifyValidationMixin


class ManifestItemForm(OtherSpecifyValidationMixin, forms.ModelForm):

    pass
