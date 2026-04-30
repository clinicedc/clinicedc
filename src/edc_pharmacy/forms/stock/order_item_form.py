from __future__ import annotations

from django import forms
from django.urls import reverse
from django.utils.html import format_html

from ...models import OrderItem


class OrderItemForm(forms.ModelForm):
    def clean(self):
        if (
            self.cleaned_data.get("container")
            and self.cleaned_data.get("container").unit_qty_max is None
        ):
            url = reverse(
                "edc_pharmacy_admin:edc_pharmacy_container_change",
                args=[self.cleaned_data.get("container").id],
            )
            errmsg = format_html(
                "Invalid. Container maximum unit quantity has not been set. "
                'Please <A href="{url}">update the container</A> before continuing.',
                url=url,
            )
            raise forms.ValidationError({"container": errmsg})
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
