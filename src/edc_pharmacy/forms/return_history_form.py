from django import forms

from ..models import ReturnHistory


class ReturnHistoryForm(forms.ModelForm):
    class Meta:
        model = ReturnHistory
        fields = "__all__"
