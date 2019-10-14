from django import forms
from edc_adverse_event.get_ae_model import get_ae_model
from edc_adverse_event.modelform_mixins import AeInitialModelFormMixin


class AeInitialForm(AeInitialModelFormMixin, forms.ModelForm):
    class Meta:
        model = get_ae_model("aeinitial")
        fields = "__all__"
