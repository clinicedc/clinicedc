from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django import forms
from django.db.models import Sum

from ...models import ReceiveItem, Stock

if TYPE_CHECKING:
    from ...models import Container


class ReceiveItemForm(forms.ModelForm):
    @property
    def container(self) -> Container | None:
        return self.cleaned_data.get("container") or self.instance.container

    @property
    def unit_qty_received(self) -> Decimal | None:
        if self.cleaned_data.get("container_unit_qty") is not None and self.cleaned_data.get(
            "item_qty_received"
        ):
            return self.cleaned_data.get("container_unit_qty") * self.cleaned_data.get(
                "item_qty_received"
            )
        return None

    @property
    def total_unit_qty_received(self) -> Decimal:
        """Returns the total received so far for this order item
        not including this transaction.
        """
        return self._meta.model.objects.filter(order_item=self.order_item).exclude(
            id=self.instance.id
        ).aggregate(unit_qty=Sum("unit_qty_received"))["unit_qty"] or Decimal("0.0")

    @property
    def unit_qty_added_to_stock(self) -> Decimal:
        """Returns the unit qty already added to stock from this receive_item"""
        if self.instance.id:
            return Stock.objects.filter(receive_item=self.instance).aggregate(
                unit_qty=Sum("unit_qty_in")
            )["unit_qty"] or Decimal("0.0")
        return Decimal("0.0")

    def clean(self):
        cleaned_data = super().clean()
        if not self.instance.id:
            if not cleaned_data.get("receive"):
                raise forms.ValidationError({"receive": "This field is required"})
            if not cleaned_data.get("order_item"):
                raise forms.ValidationError({"order_item": "This field is required"})
            if not cleaned_data.get("batch"):
                raise forms.ValidationError({"batch": "This field is required"})
            if not cleaned_data.get("reference"):
                raise forms.ValidationError({"reference": "This field is required"})
            if not cleaned_data.get("container"):
                raise forms.ValidationError({"container": "This field is required"})

        if self.container and not self.container.may_receive_as:
            raise forms.ValidationError(
                f"Container is not configured for receiving. See {self.container}."
            )

        if (
            cleaned_data.get("order_item")
            and cleaned_data.get("lot")
            and (
                cleaned_data.get("order_item").product.assignment
                != cleaned_data.get("lot").assignment
            )
        ):
            raise forms.ValidationError({"lot": "Lot assignment does not match product"})

        if self.unit_qty_received and (
            self.unit_qty_received + self.total_unit_qty_received
            > self.order_item.unit_qty_ordered
        ):
            raise forms.ValidationError(
                {
                    "item_qty_received": "Unit quantity received will be greater "
                    "than the unit quantity ordered. "
                    f"Got {self.unit_qty_received + self.total_unit_qty_received} received > "
                    f"{self.order_item.unit_qty_ordered} ordered."
                }
            )
        if self.unit_qty_added_to_stock > self.unit_qty_received:
            raise forms.ValidationError(
                {
                    "item_qty_received": "Unit quantity already added to stock exceeds "
                    "for this amount."
                    f"Got {self.unit_qty_received} received > "
                    f"{self.order_item.unit_qty_ordered} ordered."
                }
            )
        return cleaned_data

    @property
    def order_item(self):
        return self.cleaned_data.get("order_item") or self.instance.order_item

    class Meta:
        model = ReceiveItem
        fields = "__all__"
