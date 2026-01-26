from django import forms

from ...constants import CENTRAL_LOCATION
from ...models import StockTransfer


class StockTransferForm(forms.ModelForm):
    @property
    def to_location(self):
        return self.cleaned_data.get("to_location") or self.instance.to_location

    @property
    def from_location(self):
        return self.cleaned_data.get("from_location") or self.instance.from_location

    def clean(self):
        cleaned_data = super().clean()

        # assuming all fields expect 'comment' are set to readonly on EDIT
        if not self.instance.id:
            # items_qs = StockTransferItem.objects.filter(stock_transfer__pk=self.instance.pk)
            # if items_qs.count() == 0:
            #     raise forms.ValidationError("Nothing to transfer")

            # TO/FROM locations cannot be the same
            if self.to_location == self.from_location:
                raise forms.ValidationError(
                    {
                        "__all__": "Invalid location combination. 'TO' and 'FROM' locations "
                        "cannot be the same"
                    }
                )

            # at least one location must be CENTRAL
            if CENTRAL_LOCATION not in [self.to_location.name, self.from_location.name]:
                raise forms.ValidationError(
                    {"__all__": "Invalid location combination. One location must be Central"}
                )

            # check the current stock site if not the same as to_location
            # if items_qs[0].stock.location == self.to_location:
            #     raise forms.ValidationError(
            #         {
            #             "__all__": "Invalid 'TO' location. Stock is already at this location. "
            #             f"Got {self.to_location}"
            #         }
            #     )

            # if FROM central, TO must be subject's site
            # if self.from_location.name == CENTRAL_LOCATION and (
            #     items_qs[0].stock.allocation.registered_subject.site != self.to_location.site
            # ):
            #     raise forms.ValidationError(
            #         {
            #             "__all__": (
            #                 "Invalid 'TO' location. Does not match the allocated subject's "
            #                 "location / study site."
            #             )
            #         }
            #     )

            # if TO central, FROM must be subject's site
            # if self.to_location.name == CENTRAL_LOCATION and (
            #     items_qs[0].stock.allocation.registered_subject.site != self.from_location.site
            # ):
            #     raise forms.ValidationError(
            #         {
            #             "__all__": (
            #                 "Invalid 'FROM' location. Does not match the allocated subject's "
            #                 "location / study site."
            #             )
            #         }
            #     )

            # if cleaned_data.get(
            #     "item_count"
            # ) is not None and items_qs.count() > cleaned_data.get("item_count"):
            #     raise forms.ValidationError(
            #         {
            #             "__all__": (
            #                 "Invalid item count. Expected a value "
            #                 f"greater than or equal to {items_qs.count()}"
            #             )
            #         }
            #     )

        return cleaned_data

    class Meta:
        model = StockTransfer
        fields = "__all__"
        help_text = {"transfer_identifier": "(read-only)"}  # noqa: RUF012
        widgets = {  # noqa: RUF012
            "transfer_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
