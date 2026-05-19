"""Tests for ConfirmAtLocationEntryForm.

The form's job is to validate Location + Reference + Number of items
before the user is sent to the multi-page scan grid. The scan grid
itself paginates the entered count into pages of SCAN_GRID_PAGE_SIZE
inputs each (handled by the view, not the form).

Key invariants tested here:
- number_of_items must be >= 1 (IntegerField).
- number_of_items must NOT exceed unconfirmed items on the manifest.
- Entering exactly the unconfirmed count is valid (scan workflow then
  paginates).
- unconfirmed_items == 0 rejects.
- Invalid stock_transfer_identifier rejects.

DB interaction with StockTransfer is mocked — the form's role is
validation, not DB plumbing.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from edc_pharmacy.forms.stock import (
    SCAN_GRID_PAGE_SIZE,
    ConfirmAtLocationEntryForm,
)


def _make_form(**overrides):
    """Build a bound form with mocked location ModelChoiceField.

    Short-circuits the ModelChoiceField queryset lookup so the test
    doesn't need a Location row in the DB.
    """
    location = MagicMock()
    location.id = "00000000-0000-0000-0000-000000000001"
    location.__str__ = lambda self: "central"  # noqa: ARG005

    data = {
        "location": str(location.id),
        "stock_transfer_identifier": "TX0001",
        "number_of_items": 3,
    }
    data.update(overrides)

    form = ConfirmAtLocationEntryForm(data)
    form.fields["location"].to_python = lambda v: location if v else None
    form.fields["location"].validate = lambda v: None
    form.fields["location"].run_validators = lambda v: None
    return form, location


def _mock_transfer(*, unconfirmed: int) -> MagicMock:
    transfer = MagicMock()
    transfer.unconfirmed_items = unconfirmed
    transfer.transfer_identifier = "TX0001"
    return transfer


class ConfirmAtLocationEntryFormTests(SimpleTestCase):

    @patch("edc_pharmacy.forms.stock.confirm_at_location_entry_form.StockTransfer.objects.get")
    def test_valid_well_under_unconfirmed(self, mock_get):
        mock_get.return_value = _mock_transfer(unconfirmed=8)
        form, _ = _make_form(number_of_items=3)
        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(form.cleaned_data["max_allowed"], 8)
        self.assertEqual(form.cleaned_data["number_of_items"], 3)

    @patch("edc_pharmacy.forms.stock.confirm_at_location_entry_form.StockTransfer.objects.get")
    def test_valid_at_unconfirmed_within_page_size(self, mock_get):
        # Unconfirmed == 5, well below SCAN_GRID_PAGE_SIZE — single
        # grid page will suffice.
        mock_get.return_value = _mock_transfer(unconfirmed=5)
        form, _ = _make_form(number_of_items=5)
        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(form.cleaned_data["max_allowed"], 5)

    @patch("edc_pharmacy.forms.stock.confirm_at_location_entry_form.StockTransfer.objects.get")
    def test_valid_at_unconfirmed_above_page_size(self, mock_get):
        # 53 unconfirmed, user wants to scan all 53 — valid; the scan
        # workflow paginates into 6 pages (10+10+10+10+10+3).
        mock_get.return_value = _mock_transfer(unconfirmed=53)
        form, _ = _make_form(number_of_items=53)
        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(form.cleaned_data["max_allowed"], 53)

    @patch("edc_pharmacy.forms.stock.confirm_at_location_entry_form.StockTransfer.objects.get")
    def test_valid_below_unconfirmed_above_page_size(self, mock_get):
        # User has only some of the bottles in hand; can ask for a
        # smaller batch than the unconfirmed total.
        mock_get.return_value = _mock_transfer(unconfirmed=53)
        form, _ = _make_form(number_of_items=15)
        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(form.cleaned_data["max_allowed"], 53)

    @patch("edc_pharmacy.forms.stock.confirm_at_location_entry_form.StockTransfer.objects.get")
    def test_rejects_number_over_unconfirmed(self, mock_get):
        mock_get.return_value = _mock_transfer(unconfirmed=4)
        form, _ = _make_form(number_of_items=5)
        self.assertFalse(form.is_valid())
        self.assertIn("number_of_items", form.errors)
        msg = " ".join(form.errors["number_of_items"])
        self.assertIn("4", msg)

    @patch("edc_pharmacy.forms.stock.confirm_at_location_entry_form.StockTransfer.objects.get")
    def test_rejects_when_nothing_unconfirmed(self, mock_get):
        mock_get.return_value = _mock_transfer(unconfirmed=0)
        form, _ = _make_form(number_of_items=1)
        self.assertFalse(form.is_valid())
        self.assertIn("stock_transfer_identifier", form.errors)

    def test_field_rejects_zero(self):
        form, _ = _make_form(number_of_items=0)
        self.assertFalse(form.is_valid())
        self.assertIn("number_of_items", form.errors)

    def test_field_rejects_negative(self):
        form, _ = _make_form(number_of_items=-3)
        self.assertFalse(form.is_valid())
        self.assertIn("number_of_items", form.errors)

    @patch("edc_pharmacy.forms.stock.confirm_at_location_entry_form.StockTransfer.objects.get")
    def test_rejects_unknown_identifier(self, mock_get):
        from edc_pharmacy.models import StockTransfer

        mock_get.side_effect = StockTransfer.DoesNotExist
        form, _ = _make_form(stock_transfer_identifier="DOES_NOT_EXIST")
        self.assertFalse(form.is_valid())
        self.assertIn("stock_transfer_identifier", form.errors)

    def test_scan_grid_page_size_value(self):
        """Guardrail — changing this is a deliberate UX decision."""
        self.assertEqual(SCAN_GRID_PAGE_SIZE, 10)
