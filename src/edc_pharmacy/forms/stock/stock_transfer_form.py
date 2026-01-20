from django import forms

from ...constants import CENTRAL_LOCATION
from ...models import StockTransfer, StockTransferItem


class StockTransferForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        items_qs = StockTransferItem.objects.filter(stock_transfer__pk=self.instance.pk)
        if cleaned_data.get("to_location") == cleaned_data.get("from_location"):
            raise forms.ValidationError(
                {"__all__": "Invalid location combination. Locations cannot be the same"}
            )
        # at least one location must be CENTRAL
        if CENTRAL_LOCATION not in [
            cleaned_data.get("to_location").name,
            cleaned_data.get("from_location").name,
        ]:
            raise forms.ValidationError(
                {"__all__": "Invalid location combination. One location must be Central"}
            )
        # stock items can either be returned to central or transferred
        # to the site of allocation
        if (
            cleaned_data.get("to_location")
            and items_qs.count() > 0
            and not (
                (
                    items_qs[0].stock.allocation.registered_subject.site
                    == cleaned_data.get("to_location").site
                )
                or (cleaned_data.get("to_location").name == CENTRAL_LOCATION)
            )
        ):
            raise forms.ValidationError(
                {
                    "to_location": (
                        "Invalid location. Does not match the allocated location of "
                        "the stock items for this transfer."
                    )
                }
            )
        # check the current stock site if not the same as to_location
        if items_qs.count() > 0 and items_qs[0].stock.location == cleaned_data.get(
            "to_location"
        ):
            raise forms.ValidationError(
                {"to_location": "Invalid location. Stock is already at this location."}
            )
        if (
            cleaned_data.get("item_count") is not None
            and items_qs.count() > 0
            and items_qs.count() > cleaned_data.get("item_count")
        ):
            raise forms.ValidationError(
                {
                    "item_count": (
                        f"Invalid. Expected a value greater than or equal to {items_qs.count()}"
                    )
                }
            )

        return cleaned_data

    class Meta:
        model = StockTransfer
        fields = "__all__"
        help_text = {"transfer_identifier": "(read-only)"}  # noqa: RUF012
        widgets = {  # noqa: RUF012
            "transfer_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
