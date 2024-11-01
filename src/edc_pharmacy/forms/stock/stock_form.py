from django import forms

from ...models import Stock


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = "__all__"
        help_text = {"stock_identifier": "(read-only)"}
        widgets = {
            "stock_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
