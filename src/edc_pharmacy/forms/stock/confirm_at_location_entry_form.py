"""Form for the initial /confirm-at-location/ entry page.

Captures Location + Reference (manifest identifier) + Number of items
the user intends to receive in this session. The number cannot exceed
the count of unconfirmed items still on the manifest.

The scan workflow that follows is **multi-page**: the scan grid shows
at most ``SCAN_GRID_PAGE_SIZE`` inputs per page. A "Number of items"
of 53 therefore produces six pages (10 + 10 + 10 + 10 + 10 + 3).
``SCAN_GRID_PAGE_SIZE`` is a UI page-size constant, not a cap on input.

The caller passes a `location_queryset` so the form can be reused for
both the site-context (user's sites only) and central-context flows.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

from ...models import Location, StockTransfer

if TYPE_CHECKING:
    from django.db.models import QuerySet


# Number of code-input rows rendered per scan-grid page.
#
# This is a UI/UX constant — the pharmacist scans physical bottles in
# batches of this size, then the form submits, the server processes the
# batch, and the next page renders with up to this many more inputs.
#
# It is NOT a cap on the total number of items a pharmacist may scan in
# one workflow: a manifest of 53 items will produce 6 successive pages
# (10 + 10 + 10 + 10 + 10 + 3).
SCAN_GRID_PAGE_SIZE = 10


class ConfirmAtLocationEntryForm(forms.Form):
    """Entry form for /confirm-at-location/."""

    location = forms.ModelChoiceField(
        queryset=Location.objects.none(),
        label="Location",
        empty_label="-----",
    )
    stock_transfer_identifier = forms.CharField(
        label="Reference",
        max_length=36,
    )
    number_of_items = forms.IntegerField(
        label="Number of items",
        min_value=1,
        help_text=(
            "How many physical items do you intend to scan from this "
            "manifest? Cannot exceed the number of items still unconfirmed."
        ),
    )
    session_uuid = forms.CharField(
        widget=forms.HiddenInput,
        required=False,
    )

    def __init__(
        self,
        *args,
        location_queryset: QuerySet[Location] | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if location_queryset is not None:
            self.fields["location"].queryset = location_queryset
        # Add bootstrap form-control class to all visible widgets, matching
        # the convention used elsewhere in src/edc_pharmacy/forms/stock/.
        for field in self.fields.values():
            if isinstance(field.widget, forms.HiddenInput):
                continue
            existing = field.widget.attrs.get("class", "")
            if "form-control" not in existing:
                field.widget.attrs["class"] = (existing + " form-control").strip()

    def clean(self):
        cleaned = super().clean()
        location = cleaned.get("location")
        identifier = cleaned.get("stock_transfer_identifier")
        number = cleaned.get("number_of_items")

        if not location or not identifier or number is None:
            # Field-level errors already attached on at least one of the
            # required fields; skip the cross-field DB lookup since we
            # have no usable input.
            return cleaned

        try:
            stock_transfer = StockTransfer.objects.get(
                transfer_identifier=identifier,
                to_location=location,
            )
        except StockTransfer.DoesNotExist:
            self.add_error(
                "stock_transfer_identifier",
                (
                    f"Invalid Reference. Please check the manifest reference and "
                    f"delivery site. Got {identifier!r} at {location}."
                ),
            )
            return cleaned

        unconfirmed = stock_transfer.unconfirmed_items
        if unconfirmed == 0:
            self.add_error(
                "stock_transfer_identifier",
                "Nothing remains unconfirmed for this manifest.",
            )
            return cleaned

        if number is not None and number > unconfirmed:
            self.add_error(
                "number_of_items",
                (
                    f"Number of items ({number}) exceeds the {unconfirmed} "
                    "items still unconfirmed on the manifest."
                ),
            )
            return cleaned

        # Carry the resolved StockTransfer and the validated unconfirmed
        # count through to the view.
        cleaned["stock_transfer"] = stock_transfer
        cleaned["max_allowed"] = unconfirmed
        return cleaned


__all__ = ["ConfirmAtLocationEntryForm", "SCAN_GRID_PAGE_SIZE"]
