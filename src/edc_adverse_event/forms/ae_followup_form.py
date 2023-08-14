from django import forms

from ..modelform_mixins import AeFollowupModelFormMixin, AeModelFormMixin
from ..utils import get_ae_model


class AeFollowupForm(AeFollowupModelFormMixin, AeModelFormMixin, forms.ModelForm):
    class Meta(AeFollowupModelFormMixin.Meta):
        model = get_ae_model("aefollowup")
        fields = "__all__"
