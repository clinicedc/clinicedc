from __future__ import annotations

from django import forms

from ...models import OrderItem


class OrderItemForm(forms.ModelForm):
    def clean(self):
        if (
            self.cleaned_data.get("container")
            and self.cleaned_data.get("container").unit_qty_max is None
        ):
            raise forms.ValidationError(
                {
                    "container": (
                        "Invalid. Container maximum unit quantity has not been set. "
                        "Please update the container before continuing."
                    )
                }
            )
        if (
            self.cleaned_data.get("container")
            and self.cleaned_data.get("container_unit_qty") is not None
            and self.cleaned_data.get("container").unit_qty_max
            < self.cleaned_data.get("container_unit_qty")
        ):
            raise forms.ValidationError(
                {
                    "container_unit_qty": (
                        "Invalid. Container unit quantity may not exceed "
                        f"{self.cleaned_data.get('container').unit_qty_max}"
                    )
                }
            )

        if self.instance.id and self.instance.unit_qty_received > self.cleaned_data.get(
            "item_qty_ordered"
        ):
            raise forms.ValidationError(
                {
                    "item_qty_ordered": (
                        "Invalid. May not be less than the unit quantity already received "
                    )
                }
            )

    class Meta:
        model = OrderItem
        fields = "__all__"
