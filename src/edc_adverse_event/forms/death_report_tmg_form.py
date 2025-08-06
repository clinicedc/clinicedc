from django import forms

from ..modelform_mixins import DeathReportTmgModelFormMixin
from ..utils import get_ae_model


class DeathReportTmgForm(DeathReportTmgModelFormMixin, forms.ModelForm):
    class Meta(DeathReportTmgModelFormMixin.Meta):
        model = get_ae_model("deathreporttmg")
        fields = "__all__"
