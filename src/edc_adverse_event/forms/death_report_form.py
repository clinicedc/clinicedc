from django import forms

from ..get_ae_model import get_ae_model
from ..modelform_mixins import DeathReportModelFormMixin


class DeathReportForm(DeathReportModelFormMixin, forms.ModelForm):
    class Meta(DeathReportModelFormMixin.Meta):
        model = get_ae_model("deathreport")
        fields = "__all__"
