from django import forms

from ..get_ae_model import get_ae_model
from ..modelform_mixins import AeModelFormMixin, AeTmgModelFormMixin


class AeTmgForm(AeTmgModelFormMixin, AeModelFormMixin, forms.ModelForm):
    class Meta(AeTmgModelFormMixin.Meta):
        model = get_ae_model("aetmg")
        fields = "__all__"
