from django import forms

from edc_base.modelform_validators import OtherSpecifyFieldValidator


class ManifestItemForm(OtherSpecifyFieldValidator, forms.ModelForm):

    pass
