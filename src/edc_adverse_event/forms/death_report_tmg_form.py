from django import forms

from ..get_ae_model import get_ae_model
from ..modelform_mixins import DeathReportTmgModelFormMixin


class DeathReportTmgForm(DeathReportTmgModelFormMixin, forms.ModelForm):
    class Meta(DeathReportTmgModelFormMixin.Meta):
        model = get_ae_model("deathreporttmg")
        fields = "__all__"
