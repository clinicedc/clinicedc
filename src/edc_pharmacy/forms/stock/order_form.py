from django import forms

from ...models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "__all__"
        help_text = {"order_identifier": "(read-only)"}
        widgets = {
            "order_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
