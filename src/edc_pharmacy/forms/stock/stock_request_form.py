from django import forms

from ...models import StockRequest


class StockRequestForm(forms.ModelForm):
    class Meta:
        model = StockRequest
        fields = "__all__"
        help_text = {"request_identifier": "(read-only)"}
        widgets = {
            "request_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
