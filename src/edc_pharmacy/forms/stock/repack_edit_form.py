"""Form for creating/editing a RepackRequest from the repack workflow page.

from_stock is entered as a stock code (scan or type); the form resolves it
to a Stock FK on clean. container is a filtered ModelChoiceField restricted
to containers with may_repack_as=True.
"""

from __future__ import annotations

from decimal import Decimal

from django import forms

from ...models import Container, RepackRequest, Stock


class RepackEditForm(forms.Form):
    stock_code = forms.CharField(
        label="Bulk stock code",
        max_length=36,
        help_text="Scan or type the stock code of the bulk item to repack.",
    )
    container = forms.ModelChoiceField(
        queryset=Container.objects.filter(may_repack_as=True).order_by("name"),
        label="Container",
        empty_label="Select container …",
    )
    container_unit_qty = forms.DecimalField(
        label="Units per container",
        min_value=Decimal("1.0"),
        decimal_places=2,
        max_digits=10,
        required=False,
        help_text="Leave blank to use the container default.",
    )
    override_container_unit_qty = forms.BooleanField(
        label="Override container unit qty",
        required=False,
    )
    item_qty_repack = forms.IntegerField(
        label="Containers to repack",
        min_value=1,
    )

    def __init__(self, *args, instance: RepackRequest | None = None, **kwargs):
        self.instance = instance
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                existing = field.widget.attrs.get("class", "")
                if "form-control" not in existing:
                    field.widget.attrs["class"] = (existing + " form-control").strip()
        if instance and instance.pk:
            self.fields["stock_code"].initial = instance.from_stock.code
            self.fields["stock_code"].widget.attrs["readonly"] = "readonly"
            self.fields["container"].initial = instance.container
            self.fields["container_unit_qty"].initial = instance.container_unit_qty
            self.fields["override_container_unit_qty"].initial = (
                instance.override_container_unit_qty
            )
            self.fields["item_qty_repack"].initial = instance.item_qty_repack
            if (instance.item_qty_processed or 0) > 0:
                self.fields["stock_code"].widget.attrs["readonly"] = "readonly"
                self.fields["item_qty_repack"].widget.attrs["readonly"] = "readonly"
                self.fields["container"].widget.attrs["style"] = (
                    self.fields["container"].widget.attrs.get("style", "") + " pointer-events:none;"
                ).strip()

    def clean_stock_code(self):
        code = self.cleaned_data.get("stock_code", "").strip().upper()
        if self.instance and self.instance.pk:
            return code
        qs = Stock.objects.filter(code=code, confirmed=True, repack_request__isnull=True)
        if not qs.exists():
            raise forms.ValidationError(
                "No confirmed, available bulk stock found with this code."
            )
        return code

    def clean(self):
        cleaned_data = super().clean()
        code = cleaned_data.get("stock_code", "").strip().upper()

        if self.instance and self.instance.pk:
            stock = self.instance.from_stock
        else:
            try:
                stock = Stock.objects.get(code=code, confirmed=True, repack_request__isnull=True)
            except Stock.DoesNotExist:
                return cleaned_data

        cleaned_data["from_stock"] = stock

        container = cleaned_data.get("container")
        container_unit_qty = cleaned_data.get("container_unit_qty")
        override = cleaned_data.get("override_container_unit_qty", False)
        item_qty_repack = cleaned_data.get("item_qty_repack")

        if container:
            if container == stock.container:
                self.add_error("container", "Stock is already packed in this container.")

            effective_qty = container_unit_qty or container.unit_qty_default
            cleaned_data["container_unit_qty"] = effective_qty

            if not override and container_unit_qty and container_unit_qty != container.unit_qty_default:
                self.add_error(
                    "container_unit_qty",
                    f"Expected default of {container.unit_qty_default}. "
                    "Tick 'Override' to use a different value.",
                )
            if container_unit_qty and container.unit_qty_max and container_unit_qty > container.unit_qty_max:
                self.add_error("container_unit_qty", "Cannot exceed container maximum unit quantity.")
            if container_unit_qty and container_unit_qty > stock.container_unit_qty:
                self.add_error("container", "Cannot pack into a larger container.")

        if container and item_qty_repack and not (self.instance and self.instance.pk):
            effective_qty = cleaned_data.get("container_unit_qty") or container.unit_qty_default
            if effective_qty and item_qty_repack * effective_qty > stock.unit_qty:
                self.add_error(
                    "item_qty_repack",
                    f"Insufficient stock. Need {item_qty_repack * effective_qty} units "
                    f"but only {stock.unit_qty} available.",
                )

        return cleaned_data
