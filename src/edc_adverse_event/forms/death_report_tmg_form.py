from django import forms
from edc_action_item.modelform_mixins import ActionItemModelFormMixin
from edc_adverse_event.get_ae_model import get_ae_model
from edc_adverse_event.modelform_mixins import DeathReportTmgModelFormMixin


class DeathReportTmgForm(
    DeathReportTmgModelFormMixin, ActionItemModelFormMixin, forms.ModelForm
):
    class Meta:
        model = get_ae_model("deathreporttmg")
        fields = "__all__"
