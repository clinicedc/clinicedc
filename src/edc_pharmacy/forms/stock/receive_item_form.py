from django import forms
from django.db.models import Sum

from ...models import ReceiveItem


class ReceiveItemForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        unit_qty = (
            self._meta.model.objects.filter(
                order_item=cleaned_data.get("order_item")
            ).aggregate(unit_qty=Sum("unit_qty"))["unit_qty"]
            or 0.0
        )
        if (float(cleaned_data.get("qty")) * float(cleaned_data.get("container").qty)) + float(
            unit_qty
        ) > float(cleaned_data.get("order_item").unit_qty):
            raise forms.ValidationError(
                {
                    "qty": (
                        f"Exceeds `unit qty` ordered of "
                        f'{cleaned_data.get("order_item").unit_qty}. '
                        "Note: `Unit qty` is the `QTY` * `CONTAINER.QTY`"
                    )
                }
            )

        return cleaned_data

    class Meta:
        model = ReceiveItem
        fields = "__all__"
