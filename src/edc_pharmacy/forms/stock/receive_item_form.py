from django import forms
from django.db.models import Sum

from ...models import ReceiveItem


class ReceiveItemForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        container_qty = self._meta.model.objects.filter(
            order_item=cleaned_data.get("order_item")
        ).aggregate(qty=Sum("container_qty"))["qty"]
        if (
            cleaned_data.get("unit_qty") * cleaned_data.get("container").container_qty
        ) + container_qty > cleaned_data.get("order_item").container_qty:
            raise forms.ValidationError({"unit_qty": "Exceeds ordered amount"})

        return cleaned_data

    class Meta:
        model = ReceiveItem
        fields = "__all__"
