from django import forms

from edc_base.modelform_validators import OtherSpecifyFieldValidator


class BoxItemForm(OtherSpecifyFieldValidator, forms.ModelForm):

    pass
