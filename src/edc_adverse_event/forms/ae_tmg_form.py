from django import forms
from edc_action_item.modelform_mixins import ActionItemModelFormMixin
from edc_adverse_event.get_ae_model import get_ae_model
from edc_adverse_event.modelform_mixins import AeTmgModelFormMixin


class AeTmgForm(AeTmgModelFormMixin, ActionItemModelFormMixin, forms.ModelForm):
    class Meta:
        model = get_ae_model("aetmg")
        fields = "__all__"
