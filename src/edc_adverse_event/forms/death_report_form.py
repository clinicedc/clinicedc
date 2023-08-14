from django import forms

from ..modelform_mixins import DeathReportModelFormMixin
from ..utils import get_ae_model


class DeathReportForm(DeathReportModelFormMixin, forms.ModelForm):
    class Meta(DeathReportModelFormMixin.Meta):
        model = get_ae_model("deathreport")
        fields = "__all__"
