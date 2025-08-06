from django import forms

from ...models import StockTransfer, StockTransferItem


class StockTransferForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        items_qs = StockTransferItem.objects.filter(stock_transfer__pk=self.instance.pk)
        if cleaned_data.get("to_location") and items_qs.count() > 0:
            if (
                items_qs[0].stock.allocation.registered_subject.site
                != cleaned_data.get("to_location").site
            ):
                raise forms.ValidationError(
                    {
                        "to_location": (
                            "Invalid location. Does not match the intended location of "
                            "existing stock items for this transfer."
                        )
                    }
                )
        return cleaned_data

    class Meta:
        model = StockTransfer
        fields = "__all__"
        help_text = {"transfer_identifier": "(read-only)"}
        widgets = {
            "transfer_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
