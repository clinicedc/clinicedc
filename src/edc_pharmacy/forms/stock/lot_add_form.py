"""Compact Lot form for the inline 'Add lot' modal on the receive-item page.

Product and assignment are supplied by the view from the OrderItem context,
so they aren't shown to the user.
"""

from __future__ import annotations

from datetime import date

from django import forms

from ...models import Lot


class LotAddForm(forms.ModelForm):
    expiration_date = forms.DateField(
        label="Expiration date",
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        input_formats=["%Y-%m-%d"],
    )
    manufactured_date = forms.DateField(
        label="Manufactured date",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        input_formats=["%Y-%m-%d"],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply form-control to every widget except checkboxes
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                existing = field.widget.attrs.get("class", "")
                if "form-control" not in existing:
                    field.widget.attrs["class"] = (existing + " form-control").strip()

    def clean_expiration_date(self):
        d = self.cleaned_data.get("expiration_date")
        if d and d <= date.today():
            raise forms.ValidationError("Expiration date must be in the future.")
        return d

    def clean(self):
        cleaned = super().clean()
        manuf = cleaned.get("manufactured_date")
        exp = cleaned.get("expiration_date")
        if manuf and exp and manuf > exp:
            self.add_error(
                "manufactured_date", "May not be after the expiration date."
            )
        return cleaned

    class Meta:
        model = Lot
        fields = [
            "lot_no",
            "expiration_date",
            "manufactured_date",
            "manufactured_by",
            "reference",
        ]
