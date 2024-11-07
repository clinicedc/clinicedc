from django import forms
from django.core.exceptions import ObjectDoesNotExist

from ...models import RepackRequest, Stock


class RepackRequestForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("stock_identifier"):
            try:
                Stock.objects.get(stock_identifier=cleaned_data.get("stock_identifier"))
            except ObjectDoesNotExist:
                raise forms.ValidationError("Invalid stock identifier")
        if cleaned_data.get("stock_identifier") and cleaned_data.get("product"):
            try:
                Stock.objects.get(
                    stock_identifier=cleaned_data.get("stock_identifier"),
                    product=cleaned_data.get("product"),
                )
            except ObjectDoesNotExist:
                raise forms.ValidationError(
                    "Invalid combination. Stock identifier does not match product"
                )
        return cleaned_data

    class Meta:
        model = RepackRequest
        fields = "__all__"
        help_text = {
            "repack_identifier": "(read-only)",
        }
        widgets = {
            "repack_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
