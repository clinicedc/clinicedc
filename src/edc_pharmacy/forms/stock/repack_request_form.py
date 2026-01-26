from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django import forms
from edc_form_validators import FormValidator, FormValidatorMixin

from ...models import RepackRequest

if TYPE_CHECKING:
    from ...models import Container, Stock


class RepackRequestFormValidator(FormValidator):
    def clean(self):
        pass


class RepackRequestForm(FormValidatorMixin, forms.ModelForm):
    form_validator_cls = RepackRequestFormValidator

    @property
    def from_stock(self) -> Stock | None:
        return self.cleaned_data.get("from_stock") or getattr(
            self.instance, "from_stock", None
        )

    @property
    def container(self) -> Container | None:
        return self.cleaned_data.get("container") or getattr(self.instance, "container", None)

    @property
    def container_unit_qty(self) -> Decimal | None:
        return self.cleaned_data.get("container_unit_qty") or self.container.unit_qty_default

    @property
    def override_container_unit_qty(self) -> Decimal | None:
        return (
            self.cleaned_data.get("override_container_unit_qty")
            or self.instance.override_container_unit_qty
        )

    def clean(self):
        cleaned_data = super().clean()
        if (
            self.instance.id
            and cleaned_data.get("item_qty_repack") != self.instance.item_qty_repack
        ):
            raise forms.ValidationError(
                "Number of containers to repack may not be changed after processing"
            )
        if (
            self.from_stock
            and self.container
            and cleaned_data.get("item_qty_repack") is not None
        ):
            if self.from_stock and not getattr(self.from_stock, "confirmation", None):
                raise forms.ValidationError(
                    {
                        "from_stock": (
                            "Unconfirmed stock item. Only confirmed "
                            "stock items may be used to repack"
                        )
                    }
                )
            if self.container and self.container == self.from_stock.container:
                raise forms.ValidationError(
                    {"container": "Stock is already packed in this container."}
                )

            if (
                not self.override_container_unit_qty
                and self.container_unit_qty != self.container.unit_qty_default
            ):
                raise forms.ValidationError(
                    {
                        "container_unit_qty": (
                            "Invalid. Expected default container value of "
                            f"{self.container.unit_qty_default}."
                        )
                    }
                )
            if (
                self.container_unit_qty
                and self.container_unit_qty > self.container.unit_qty_max
            ):
                raise forms.ValidationError(
                    {"container_unit_qty": "Cannot exceed container maximum unit quantity."}
                )

            if (
                self.container_unit_qty
                and self.container_unit_qty > self.from_stock.container_unit_qty
            ):
                raise forms.ValidationError(
                    {"container": "Cannot pack into larger container."}
                )
            if (
                cleaned_data.get("item_qty_repack")
                and self.instance.item_qty_processed
                and cleaned_data.get("item_qty_repack") < self.instance.item_qty_processed
            ):
                raise forms.ValidationError(
                    {
                        "item_qty_repack": "Cannot be less than the number of containers processed"
                    }
                )

            if not self.instance.id and (
                cleaned_data.get("item_qty_repack") * self.container_unit_qty
                > self.from_stock.unit_qty
            ):
                needed_qty = cleaned_data.get("item_qty_repack") * self.container_unit_qty
                on_hand_qty = self.from_stock.unit_qty
                raise forms.ValidationError(
                    {
                        "item_qty_repack": (
                            "Insufficient unit quantity to repack from this stock item. "
                            f"Need {needed_qty} units but have only {on_hand_qty} units on hand"
                        )
                    }
                )

        return cleaned_data

    class Meta:
        model = RepackRequest
        fields = "__all__"
        help_text = {  # noqa: RUF012
            "repack_identifier": "(read-only)",
        }
        widgets = {  # noqa: RUF012
            "repack_identifier": forms.TextInput(attrs={"readonly": "readonly"}),
        }
