"""Form for adding or editing an OrderItem from the order management page.

Excludes AUDIT_MODEL_FIELDS (SYSTEM_COLUMNS), the auto-assigned
order_item_identifier, and the signal-maintained qty fields
(unit_qty_ordered / unit_qty_pending / unit_qty_received) and status.

The parent ``order`` is supplied via the view, never via the form.
"""

from __future__ import annotations

from decimal import Decimal

from django import forms

from ...models import OrderItem


class OrderItemAddForm(forms.ModelForm):
    def __init__(self, *args, order=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.order = order
        # Apply form-control to every widget except checkboxes
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                existing = field.widget.attrs.get("class", "")
                if "form-control" not in existing:
                    field.widget.attrs["class"] = (existing + " form-control").strip()

    def clean(self):
        cleaned = super().clean()
        container = cleaned.get("container")
        container_unit_qty = cleaned.get("container_unit_qty")
        item_qty_ordered = cleaned.get("item_qty_ordered")

        if container and container.unit_qty_max is None:
            raise forms.ValidationError(
                {
                    "container": (
                        "Container maximum unit quantity has not been set. "
                        "Please update the container before continuing."
                    )
                }
            )
        if (
            container
            and container_unit_qty is not None
            and container.unit_qty_max < container_unit_qty
        ):
            raise forms.ValidationError(
                {
                    "container_unit_qty": (
                        "May not exceed the container maximum "
                        f"({container.unit_qty_max})."
                    )
                }
            )
        # When editing an existing item, can't drop quantity below already-received
        if (
            self.instance
            and self.instance.pk
            and item_qty_ordered is not None
            and container_unit_qty is not None
        ):
            new_unit_qty = Decimal(item_qty_ordered) * container_unit_qty
            received = self.instance.unit_qty_received or Decimal("0.0")
            if received > new_unit_qty:
                raise forms.ValidationError(
                    {
                        "item_qty_ordered": (
                            "May not be less than the quantity already received "
                            f"({received})."
                        )
                    }
                )
        return cleaned

    class Meta:
        model = OrderItem
        fields = [
            "product",
            "container",
            "container_unit_qty",
            "item_qty_ordered",
        ]
