from django import forms

from ..models import StockCreateLabels


class StockCreateLabelsForm(forms.ModelForm):
    class Meta:
        model = StockCreateLabels
        fields = "__all__"
