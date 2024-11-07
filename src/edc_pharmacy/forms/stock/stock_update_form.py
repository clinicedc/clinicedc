from django import forms

from ...models import StockUpdate


class StockUpdateForm(forms.ModelForm):
    class Meta:
        model = StockUpdate
        fields = "__all__"
        help_text = {
            "update_identifier": "(read-only)",
        }
        widgets = {
            "update_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
