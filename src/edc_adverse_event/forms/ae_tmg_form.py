from django import forms

from ..modelform_mixins import AeModelFormMixin, AeTmgModelFormMixin
from ..utils import get_ae_model


class AeTmgForm(AeTmgModelFormMixin, AeModelFormMixin, forms.ModelForm):
    class Meta(AeTmgModelFormMixin.Meta):
        model = get_ae_model("aetmg")
        fields = "__all__"
