from django import forms

from ..get_ae_model import get_ae_model
from ..modelform_mixins import AeFollowupModelFormMixin, AeModelFormMixin


class AeFollowupForm(AeFollowupModelFormMixin, AeModelFormMixin, forms.ModelForm):
    class Meta(AeFollowupModelFormMixin.Meta):
        model = get_ae_model("aefollowup")
        fields = "__all__"
