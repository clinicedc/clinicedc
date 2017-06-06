from django import forms

from edc_base.modelform_mixins import OtherSpecifyValidationMixin


class BoxItemForm(OtherSpecifyValidationMixin, forms.ModelForm):

    pass
