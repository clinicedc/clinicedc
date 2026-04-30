"""Form for creating a StockTransfer from the workflow page."""

from __future__ import annotations

from django import forms

from ...models import Location, StockTransfer


class StockTransferEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["from_location"].queryset = Location.objects.order_by("display_name")
        self.fields["to_location"].queryset = Location.objects.filter(
            site_id__isnull=False
        ).order_by("display_name")
        for field in self.fields.values():
            if not isinstance(field.widget, forms.Textarea):
                existing = field.widget.attrs.get("class", "")
                if "form-control" not in existing:
                    field.widget.attrs["class"] = (existing + " form-control").strip()

    def clean(self):
        cleaned_data = super().clean()
        if (
            cleaned_data.get("from_location")
            and cleaned_data.get("to_location")
            and cleaned_data["from_location"] == cleaned_data["to_location"]
        ):
            raise forms.ValidationError("From and To locations cannot be the same.")
        # Once items have been scanned/transferred, lock from/to locations
        # and don't let item_count drop below the scanned count.
        if self.instance and self.instance.pk:
            scanned = self.instance.stocktransferitem_set.count()
            if scanned > 0:
                if cleaned_data.get("from_location") != self.instance.from_location:
                    self.add_error(
                        "from_location",
                        "Cannot change once items have been transferred.",
                    )
                if cleaned_data.get("to_location") != self.instance.to_location:
                    self.add_error(
                        "to_location",
                        "Cannot change once items have been transferred.",
                    )
                item_count = cleaned_data.get("item_count")
                if item_count is not None and item_count < scanned:
                    self.add_error(
                        "item_count",
                        f"May not be less than the number already scanned ({scanned}).",
                    )
        return cleaned_data

    class Meta:
        model = StockTransfer
        fields = ("from_location", "to_location", "item_count", "comment")
        widgets = {"comment": forms.Textarea(attrs={"rows": 3})}  # noqa: RUF012
