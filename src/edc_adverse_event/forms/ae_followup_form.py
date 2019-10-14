from django import forms
from edc_adverse_event.get_ae_model import get_ae_model
from edc_adverse_event.modelform_mixins import AeFollowupModelFormMixin


class AeFollowupForm(AeFollowupModelFormMixin, forms.ModelForm):
    class Meta:
        model = get_ae_model("aefollowup")
        fields = "__all__"
