from django import forms

from ...models import Supplier


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = "__all__"
        help_text = {"supplier_identifier": "(read-only)"}
        widgets = {
            "supplier_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
