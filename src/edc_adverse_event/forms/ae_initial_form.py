from django import forms

from ..get_ae_model import get_ae_model
from ..modelform_mixins import AeInitialModelFormMixin, AeModelFormMixin


class AeInitialForm(AeInitialModelFormMixin, AeModelFormMixin, forms.ModelForm):
    class Meta(AeInitialModelFormMixin.Meta):
        model = get_ae_model("aeinitial")
        fields = "__all__"
