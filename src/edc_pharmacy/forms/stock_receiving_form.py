from django import forms

from ..models import StockReceiving


class StockReceivingForm(forms.ModelForm):
    class Meta:
        model = StockReceiving
        fields = "__all__"
