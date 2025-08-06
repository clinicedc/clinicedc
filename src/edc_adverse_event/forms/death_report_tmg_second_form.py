from django import forms

from ..modelform_mixins import DeathReportTmgSecondModelFormMixin
from ..utils import get_ae_model


class DeathReportTmgSecondForm(DeathReportTmgSecondModelFormMixin, forms.ModelForm):
    class Meta(DeathReportTmgSecondModelFormMixin.Meta):
        model = get_ae_model("deathreporttmgsecond")
        fields = "__all__"
