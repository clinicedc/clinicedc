from django import forms

from ..models import ActionType


class ActionTypeForm(forms.ModelForm):
    class Meta:
        model = ActionType
        fields = "__all__"
