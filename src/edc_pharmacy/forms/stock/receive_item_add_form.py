from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django import forms
from django.db.models import Sum

from ...models import Container, Lot, ReceiveItem

if TYPE_CHECKING:
    from ...models import OrderItem


class ReceiveItemAddForm(forms.Form):
    """Lightweight form for adding a ReceiveItem from the receive-order page.

    Instantiate with the target ``order_item`` so the lot queryset can be
    filtered to the correct product/assignment and the container pre-selected.
    """

    lot = forms.ModelChoiceField(
        queryset=Lot.objects.none(),
        label="Lot # / Batch",
        empty_label="Select lot # / batch …",
        help_text="Available lot #'s based on the order",
    )
    container = forms.ModelChoiceField(
        queryset=Container.objects.filter(may_receive_as=True),
        label="Container",
    )
    container_unit_qty = forms.DecimalField(
        label="Units per container",
        min_value=Decimal("1.0"),
        decimal_places=2,
        max_digits=10,
    )
    item_qty_received = forms.IntegerField(
        label="Containers received",
        min_value=1,
    )
    reference = forms.CharField(
        label="Reference",
        max_length=150,
        required=False,
        initial="-",
    )

    def __init__(
        self,
        *args,
        order_item: OrderItem = None,
        instance: ReceiveItem | None = None,
        **kwargs,
    ):
        self.order_item = order_item
        self.instance = instance
        super().__init__(*args, **kwargs)
        if order_item:
            self.fields["lot"].queryset = Lot.objects.filter(
                product=order_item.product
            ).order_by("-expiration_date")
            if not instance:
                self.fields["container"].initial = order_item.container
                self.fields["container_unit_qty"].initial = order_item.container_unit_qty
        # Pre-fill from existing instance for edit mode
        if instance:
            self.fields["lot"].initial = instance.lot
            self.fields["container"].initial = instance.container
            self.fields["container_unit_qty"].initial = instance.container_unit_qty
            self.fields["item_qty_received"].initial = instance.item_qty_received
            self.fields["reference"].initial = instance.reference
        # Apply form-control to every widget except checkboxes
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                existing = field.widget.attrs.get("class", "")
                if "form-control" not in existing:
                    field.widget.attrs["class"] = (existing + " form-control").strip()

    def clean(self):
        cleaned_data = super().clean()
        lot = cleaned_data.get("lot")
        container_unit_qty = cleaned_data.get("container_unit_qty")
        item_qty_received = cleaned_data.get("item_qty_received")

        if (
            lot
            and self.order_item
            and lot.product.assignment != self.order_item.product.assignment
        ):
            self.add_error(
                "lot", "Assignment for this lot # / batch does not match the order."
            )

        if container_unit_qty and item_qty_received and self.order_item:
            unit_qty_this = container_unit_qty * item_qty_received
            existing_qs = ReceiveItem.objects.filter(order_item=self.order_item)
            # Exclude the row being edited so its old value isn't double-counted
            if self.instance and self.instance.pk:
                existing_qs = existing_qs.exclude(pk=self.instance.pk)
            already_received = existing_qs.aggregate(total=Sum("unit_qty_received"))[
                "total"
            ] or Decimal("0.0")
            if unit_qty_this + already_received > self.order_item.unit_qty_ordered:
                self.add_error(
                    "item_qty_received",
                    f"Receiving {unit_qty_this} units would exceed the ordered quantity. "
                    f"Ordered: {self.order_item.unit_qty_ordered}, "
                    f"already received: {already_received}.",
                )
        return cleaned_data
