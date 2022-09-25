from django import forms

from ..get_ae_model import get_ae_model
from ..modelform_mixins import AeModelFormMixin, AeSusarModelFormMixin


class AeSusarForm(AeSusarModelFormMixin, AeModelFormMixin, forms.ModelForm):
    class Meta(AeSusarModelFormMixin.Meta):
        model = get_ae_model("aesusar")
        fields = "__all__"
