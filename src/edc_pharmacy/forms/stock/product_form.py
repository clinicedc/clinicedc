from django import forms

from ...models import Product, Stock


class ProductForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        if (
            getattr(self.instance, "id", None)
            and Stock.objects.filter(product=self.instance).exists()
        ):
            raise forms.ValidationError("Product is in use and cannot be changed.")
        return cleaned_data

    class Meta:
        model = Product
        fields = "__all__"
        help_text = {"product_identifier": "(read-only)"}
        widgets = {
            "product_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
