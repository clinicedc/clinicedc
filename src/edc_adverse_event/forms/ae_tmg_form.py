from django import forms
from edc_action_item.modelform_mixins import ActionItemModelFormMixin

from ..get_ae_model import get_ae_model
from .mixins import AeTmgModelFormMixin


class AeTmgForm(AeTmgModelFormMixin, ActionItemModelFormMixin, forms.ModelForm):
    class Meta:
        model = get_ae_model("aetmg")
        fields = "__all__"
