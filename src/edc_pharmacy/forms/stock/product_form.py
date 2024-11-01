from django import forms

from ...models import Product


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = "__all__"
        help_text = {"product_identifier": "(read-only)"}
        widgets = {
            "product_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
