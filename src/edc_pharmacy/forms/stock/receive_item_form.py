from decimal import Decimal

from django import forms
from django.db.models import Sum

from ...models import ReceiveItem


class ReceiveItemForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        if not self.instance.id:
            if not cleaned_data.get("receive"):
                raise forms.ValidationError({"receive": "This field is required"})
            if not cleaned_data.get("order_item"):
                raise forms.ValidationError({"order_item": "This field is required"})
            if not cleaned_data.get("container"):
                raise forms.ValidationError({"container": "This field is required"})

        if cleaned_data.get("order_item") and cleaned_data.get("lot"):
            if (
                cleaned_data.get("order_item").product.assignment
                != cleaned_data.get("lot").assignment
            ):
                raise forms.ValidationError({"lot": "Lot assignment does not match product"})

        # in unit_qty's
        if cleaned_data.get("qty"):
            # TODO: clean this up
            qty_ordered = self.order_item.unit_qty + (self.order_item.unit_qty_received or 0)
            qty_already_received = self._meta.model.objects.filter(
                order_item=self.order_item
            ).aggregate(unit_qty=Sum("unit_qty"))["unit_qty"] or Decimal(0)
            qty_available = qty_ordered - qty_already_received
            qty_to_receive = cleaned_data.get("qty") * cleaned_data.get("container").qty
            if qty_to_receive > qty_available:
                raise forms.ValidationError(
                    {
                        "qty": (
                            f"Exceeds `unit qty` ordered of "
                            f"{self.order_item.unit_qty}. "
                            f"Got {qty_to_receive} but only "
                            f"{qty_available} are still on order."
                        )
                    }
                )

        return cleaned_data

    @property
    def order_item(self):
        return self.cleaned_data.get("order_item") or self.instance.order_item

    class Meta:
        model = ReceiveItem
        fields = "__all__"
