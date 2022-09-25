from django import forms

from ..get_ae_model import get_ae_model
from ..modelform_mixins import DeathReportTmgSecondModelFormMixin


class DeathReportTmgSecondForm(DeathReportTmgSecondModelFormMixin, forms.ModelForm):
    class Meta(DeathReportTmgSecondModelFormMixin.Meta):
        model = get_ae_model("deathreporttmgsecond")
        fields = "__all__"
