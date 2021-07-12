from django import forms
from edc_action_item.modelform_mixins import ActionItemModelFormMixin

from ..get_ae_model import get_ae_model
from .mixins import DeathReportTmgModelFormMixin


class DeathReportTmgSecondForm(
    DeathReportTmgModelFormMixin, ActionItemModelFormMixin, forms.ModelForm
):
    class Meta:
        model = get_ae_model("deathreporttmgsecond")
        fields = "__all__"
