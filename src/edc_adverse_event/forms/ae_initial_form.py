from django import forms

from ..modelform_mixins import AeInitialModelFormMixin, AeModelFormMixin
from ..utils import get_ae_model


class AeInitialForm(AeInitialModelFormMixin, AeModelFormMixin, forms.ModelForm):
    class Meta(AeInitialModelFormMixin.Meta):
        model = get_ae_model("aeinitial")
        fields = "__all__"
