from django import forms

from ...models import Stock


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = "__all__"
        help_text = {  # noqa: RUF012
            "stock_identifier": "(read-only)",
            "receive_item": "(read-only)",
            "container": "(read-only)",
        }
        widgets = {  # noqa: RUF012
            "stock_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
            "receive_item": forms.TextInput(attrs={"readonly": "readonly"}),
            "container": forms.TextInput(attrs={"readonly": "readonly"}),
        }
