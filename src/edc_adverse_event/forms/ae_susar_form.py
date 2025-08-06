from django import forms

from ..modelform_mixins import AeModelFormMixin, AeSusarModelFormMixin
from ..utils import get_ae_model


class AeSusarForm(AeSusarModelFormMixin, AeModelFormMixin, forms.ModelForm):
    class Meta(AeSusarModelFormMixin.Meta):
        model = get_ae_model("aesusar")
        fields = "__all__"
