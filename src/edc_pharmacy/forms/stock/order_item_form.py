from django import forms

from ...models import OrderItem


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ["product", "container", "unit_qty"]
        help_text = {"order": "(read-only)"}
        widgets = {
            "order": forms.TextInput(attrs={"readonly": "readonly"}),
        }
