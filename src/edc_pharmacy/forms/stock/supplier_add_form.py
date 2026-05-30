"""Form for adding/editing a Supplier from the order edit page.

Excludes AUDIT_MODEL_FIELDS (SYSTEM_COLUMNS).
"""

from django import forms

from ...models import Supplier


class SupplierAddForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply form-control to every widget except checkboxes
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                existing = field.widget.attrs.get("class", "")
                if "form-control" not in existing:
                    field.widget.attrs["class"] = (existing + " form-control").strip()

    class Meta:
        model = Supplier
        fields = (
            "name",
            "contact",
            "telephone",
            "email",
            "address_one",
            "address_two",
            "city",
            "postal_code",
            "state",
            "country",
        )
