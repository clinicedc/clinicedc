from django import forms

from ...models import StockTransfer


class StockTransferForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()

        return cleaned_data

    class Meta:
        model = StockTransfer
        fields = "__all__"
        help_text = {"transfer_identifier": "(read-only)"}
        widgets = {
            "transfer_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
