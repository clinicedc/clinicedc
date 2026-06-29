"""Tests for resolving stock take discrepancies.

Covers the ResolveStockTakeItemView endpoint, which applies a correction to a
single StockTakeItem and links the resulting StockTransaction (auditable
resolution link, issue #123 PR1).
"""

from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.action_items import register_actions
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.sites import all_sites
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.test import TestCase, override_settings, tag
from django.urls import reverse
from django.utils import timezone

from edc_consent import site_consents
from edc_facility.import_holidays import import_holidays
from edc_pharmacy.constants import (
    CENTRAL_LOCATION,
    TXN_BIN_MOVED,
    TXN_LOST,
    TXN_STORED,
)
from edc_pharmacy.models import (
    MATCHED,
    MISSING,
    UNEXPECTED,
    Assignment,
    Container,
    ContainerType,
    ContainerUnits,
    Formulation,
    FormulationType,
    Location,
    Lot,
    Medication,
    Order,
    OrderItem,
    Product,
    Receive,
    ReceiveItem,
    Route,
    Stock,
    StockTake,
    StockTakeItem,
    StorageBin,
    StorageBinItem,
    Units,
)
from edc_pharmacy.transaction_log import apply_delta_context, apply_transaction
from edc_pharmacy.utils import confirm_stock
from edc_pharmacy.views.stock_take_conflicts import annotate_conflicts
from edc_randomization.constants import ACTIVE
from edc_sites.site import sites
from edc_sites.utils import add_or_update_django_sites
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

utc_tz = ZoneInfo("UTC")

User = get_user_model()


@tag("stock_take_resolve")
@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=utc_tz))
@override_settings(SITE_ID=10)
class TestStockTakeResolve(TestCase):
    username = "aroy"

    @classmethod
    def setUpTestData(cls):
        import_holidays()
        sites._registry = {}
        sites.loaded = False
        User.objects.create_user(
            cls.username,
            is_staff=True,
            is_active=True,
            is_superuser=True,
            email="me@example.com",
        )
        sites.register(*all_sites)
        add_or_update_django_sites()
        register_actions()

    def setUp(self):
        site_consents.registry = {}
        site_consents.loaded = False
        site_consents.register(consent_v1)
        self.user = User.objects.get(username=self.username)

        visit_schedule = get_visit_schedule(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)

        self.actor = self.user
        self.location_central, _ = Location.objects.get_or_create(
            name=CENTRAL_LOCATION, defaults={"display_name": "Take Test Central"}
        )
        self.location_site, _ = Location.objects.get_or_create(
            name="take_test_site",
            defaults={"display_name": "Take Test Site", "site": Site.objects.get(id=10)},
        )

        medication = Medication.objects.create(name="paracetamol")
        formulation = Formulation.objects.create(
            medication=medication,
            strength=500,
            units=Units.objects.get(name="mg"),
            route=Route.objects.get(display_name="Oral"),
            formulation_type=FormulationType.objects.get(display_name__iexact="Tablet"),
        )
        assignment = Assignment.objects.create(name=ACTIVE)
        product = Product.objects.create(formulation=formulation, assignment=assignment)
        lot = Lot.objects.create(
            lot_no="TEST001",
            assignment=assignment,
            expiration_date=timezone.now() + relativedelta(years=1),
            product=product,
        )

        container_units, _ = ContainerUnits.objects.get_or_create(
            name="tablet", plural_name="tablets"
        )
        container_type_tablet, _ = ContainerType.objects.get_or_create(name="tablet_tk")
        container_type_bottle, _ = ContainerType.objects.get_or_create(name="bottle_tk")
        container_order = Container.objects.create(
            name="tk_tablet",
            display_name="Take Test Tablet",
            container_type=container_type_tablet,
            unit_qty_default=1,
            units=container_units,
            may_order_as=True,
        )
        self.container = Container.objects.create(
            name="tk_bottle_100",
            display_name="Take Test Bottle of 100",
            container_type=container_type_bottle,
            unit_qty_default=100,
            units=container_units,
            may_receive_as=True,
        )

        order = Order.objects.create(order_datetime=timezone.now())
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            item_qty_ordered=10,
            container_unit_qty=container_order.unit_qty_default,
            container=container_order,
        )
        receive = Receive.objects.create(order=order, location=self.location_central)
        ReceiveItem.objects.create(
            receive=receive,
            order_item=order_item,
            item_qty_received=3,
            container_unit_qty=self.container.unit_qty_default,
            container=self.container,
            lot=lot,
        )

        codes = list(Stock.objects.values_list("code", flat=True))
        confirm_stock(
            receive,
            codes,
            fk_attr="receive_item__receive",
            user_created="aroy",
            actor=self.user,
        )

        # Two bins at the same site location.
        self.bin_a = StorageBin.objects.create(
            container=self.container, location=self.location_site
        )
        self.bin_b = StorageBin.objects.create(
            container=self.container, location=self.location_site
        )

        # Drive all stock to stored_at_location=True at the site.
        stocks = list(Stock.objects.order_by("code"))
        # bin_a holds the first two, bin_b holds the third.
        self.stock_matched, self.stock_missing, self.stock_unexpected = stocks
        for stock, storage_bin in (
            (self.stock_matched, self.bin_a),
            (self.stock_missing, self.bin_a),
            (self.stock_unexpected, self.bin_b),
        ):
            with apply_delta_context():
                stock.location = self.location_site
                stock.save(update_fields=["location"])
            apply_transaction(stock, TXN_STORED, self.actor, storage_bin=storage_bin)

        # A stock take for bin_a with one of each outcome.
        self.stock_take = StockTake.objects.create(
            storage_bin=self.bin_a, performed_by=self.user
        )
        self.item_matched = StockTakeItem.objects.create(
            stock_take=self.stock_take,
            stock=self.stock_matched,
            code=self.stock_matched.code,
            status=MATCHED,
        )
        self.item_missing = StockTakeItem.objects.create(
            stock_take=self.stock_take,
            stock=self.stock_missing,
            code=self.stock_missing.code,
            status=MISSING,
        )
        self.item_unexpected = StockTakeItem.objects.create(
            stock_take=self.stock_take,
            stock=self.stock_unexpected,
            code=self.stock_unexpected.code,
            status=UNEXPECTED,
        )
        self.item_foreign = StockTakeItem.objects.create(
            stock_take=self.stock_take,
            stock=None,
            code="FOREIGN1",
            status=UNEXPECTED,
        )
        self.client.force_login(self.user)

    def _url(self, item):
        return reverse(
            "edc_pharmacy:resolve_stock_take_item_url",
            kwargs={"stock_take_item": item.pk},
        )

    def _post(self, item, **data):
        return self.client.post(self._url(item), data)

    # ------------------------------------------------------------------

    def test_resolve_missing_as_lost(self):
        response = self._post(self.item_missing, action="lost", reason="not on shelf")
        self.assertEqual(response.status_code, 302)
        self.item_missing.refresh_from_db()
        self.assertTrue(self.item_missing.resolved)
        self.assertEqual(self.item_missing.stock_transaction.transaction_type, TXN_LOST)
        self.assertEqual(self.item_missing.stock_transaction.stock_id, self.stock_missing.pk)
        self.stock_missing.refresh_from_db()
        self.assertTrue(self.stock_missing.lost)

    def test_resolve_unexpected_add_to_bin_auto_reason(self):
        # No reason posted — the add action auto-generates the audit note.
        response = self._post(self.item_unexpected, action="move_to_bin")
        self.assertEqual(response.status_code, 302)
        self.item_unexpected.refresh_from_db()
        self.assertTrue(self.item_unexpected.resolved)
        txn = self.item_unexpected.stock_transaction
        self.assertEqual(txn.transaction_type, TXN_BIN_MOVED)
        self.assertIn(self.bin_a.bin_identifier, txn.reason)
        self.assertIn(self.stock_take.stock_take_identifier, txn.reason)
        # the ledger records where it moved from (bin_b) and to (bin_a)
        self.assertEqual(txn.from_bin_id, self.bin_b.pk)
        self.assertEqual(txn.to_bin_id, self.bin_a.pk)
        # StorageBinItem for the stock now points at bin_a (the take's bin).
        sbi = StorageBinItem.objects.get(stock=self.stock_unexpected)
        self.assertEqual(sbi.storage_bin_id, self.bin_a.pk)

    def test_undo_add_returns_item_to_original_bin(self):
        self._post(self.item_unexpected, action="move_to_bin")
        self.item_unexpected.refresh_from_db()
        self.assertTrue(self.item_unexpected.resolved)
        # Undo
        response = self._post(self.item_unexpected, action="undo")
        self.assertEqual(response.status_code, 302)
        self.item_unexpected.refresh_from_db()
        # discrepancy is re-opened
        self.assertFalse(self.item_unexpected.resolved)
        # item is back in its original bin (bin_b)
        sbi = StorageBinItem.objects.get(stock=self.stock_unexpected)
        self.assertEqual(sbi.storage_bin_id, self.bin_b.pk)
        # a compensating BIN_MOVED was written (forward + undo = 2 on this stock)
        self.assertEqual(
            self.stock_unexpected.transactions.filter(
                transaction_type=TXN_BIN_MOVED
            ).count(),
            2,
        )

    def test_undo_rejected_for_non_bin_move(self):
        # resolve a missing item as lost, then attempt undo -> rejected
        self._post(self.item_missing, action="lost", reason="x")
        self.item_missing.refresh_from_db()
        txn_id = self.item_missing.stock_transaction_id
        response = self._post(self.item_missing, action="undo")
        self.assertEqual(response.status_code, 302)
        self.item_missing.refresh_from_db()
        # still resolved, link unchanged
        self.assertEqual(self.item_missing.stock_transaction_id, txn_id)

    def test_undo_on_unresolved_is_noop(self):
        response = self._post(self.item_unexpected, action="undo")
        self.assertEqual(response.status_code, 302)
        self.item_unexpected.refresh_from_db()
        self.assertFalse(self.item_unexpected.resolved)

    def test_reason_is_required(self):
        response = self._post(self.item_missing, action="lost")
        self.assertEqual(response.status_code, 302)
        self.item_missing.refresh_from_db()
        self.assertFalse(self.item_missing.resolved)

    def test_invalid_action_for_missing(self):
        response = self._post(self.item_missing, action="move_to_bin", reason="x")
        self.assertEqual(response.status_code, 302)
        self.item_missing.refresh_from_db()
        self.assertFalse(self.item_missing.resolved)

    def test_invalid_action_for_unexpected(self):
        response = self._post(self.item_unexpected, action="lost", reason="x")
        self.assertEqual(response.status_code, 302)
        self.item_unexpected.refresh_from_db()
        self.assertFalse(self.item_unexpected.resolved)

    def test_not_in_system_cannot_resolve(self):
        response = self._post(self.item_foreign, action="move_to_bin", reason="x")
        self.assertEqual(response.status_code, 302)
        self.item_foreign.refresh_from_db()
        self.assertFalse(self.item_foreign.resolved)

    def test_matched_cannot_resolve(self):
        response = self._post(self.item_matched, action="lost", reason="x")
        self.assertEqual(response.status_code, 302)
        self.item_matched.refresh_from_db()
        self.assertFalse(self.item_matched.resolved)

    def test_already_resolved_is_noop(self):
        self._post(self.item_missing, action="lost", reason="first")
        self.item_missing.refresh_from_db()
        first_txn_id = self.item_missing.stock_transaction_id
        self.assertIsNotNone(first_txn_id)
        # Second attempt should not change the link.
        self._post(self.item_missing, action="damaged", reason="second")
        self.item_missing.refresh_from_db()
        self.assertEqual(self.item_missing.stock_transaction_id, first_txn_id)

    def test_redirects_to_next_when_provided(self):
        next_url = reverse("edc_pharmacy:stock_take_home_url")
        response = self.client.post(
            self._url(self.item_missing),
            {"action": "lost", "reason": "x", "next": next_url},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, next_url)

    # -- resolution-actions partial (PR2 UI) ---------------------------

    def _render_actions(self, item):
        return render_to_string(
            "edc_pharmacy/stock/_resolve_actions.html",
            {"item": item, "next_url": "/next/"},
        )

    def test_partial_open_unexpected_shows_move_form(self):
        html = self._render_actions(self.item_unexpected)
        self.assertIn("move_to_bin", html)
        self.assertIn("Add to bin", html)
        # no reason input for the add action — the note is auto-generated
        self.assertNotIn('name="reason"', html)

    def test_partial_not_in_system_shows_acknowledge(self):
        html = self._render_actions(self.item_foreign)
        self.assertIn('value="acknowledge"', html)
        self.assertIn("Acknowledge", html)
        self.assertIn('placeholder="Reason (audit note)"', html)
        self.assertNotIn("Add to bin", html)

    def test_cannot_add_reason_property(self):
        # binnable unexpected (stored, not terminal) and missing -> no reason
        self.assertEqual(self.item_unexpected.cannot_add_reason, "")
        self.assertEqual(self.item_missing.cannot_add_reason, "")
        # not in the system
        self.assertEqual(self.item_foreign.cannot_add_reason, "not in the system")
        # terminal stock
        apply_transaction(self.stock_unexpected, TXN_LOST, self.user, reason="x")
        self.item_unexpected.refresh_from_db()
        self.assertEqual(self.item_unexpected.cannot_add_reason, "already lost")

    def test_partial_resolved_missing_links_to_ledger(self):
        self._post(self.item_missing, action="lost", reason="not on shelf")
        self.item_missing.refresh_from_db()
        html = self._render_actions(self.item_missing)
        self.assertIn("Resolved", html)
        self.assertNotIn("Undo", html)
        # links to the ledger filtered by this code, not the admin txn form
        ledger_url = reverse("edc_pharmacy:ledger_url")
        self.assertIn(f"{ledger_url}?q={self.item_missing.code}", html)

    def test_partial_resolved_unexpected_shows_undo(self):
        self._post(self.item_unexpected, action="move_to_bin")
        self.item_unexpected.refresh_from_db()
        html = self._render_actions(self.item_unexpected)
        self.assertIn("Resolved", html)
        self.assertIn("Undo", html)
        self.assertIn('value="undo"', html)

    # -- cross-bin conflict detection ----------------------------------

    def test_conflict_missing_also_unexpected_elsewhere(self):
        # The same code is scanned as unexpected in bin_b's take.
        take_b = StockTake.objects.create(
            storage_bin=self.bin_b, performed_by=self.user
        )
        item_unexpected_b = StockTakeItem.objects.create(
            stock_take=take_b,
            stock=self.stock_missing,
            code=self.stock_missing.code,
            status=UNEXPECTED,
        )
        annotate_conflicts([self.item_missing, item_unexpected_b])
        # missing row is warned not to mark it lost
        self.assertEqual(self.item_missing.conflict_level, "warning")
        self.assertIn(self.bin_b.bin_identifier, self.item_missing.conflict)
        self.assertIn("misfiled", self.item_missing.conflict)
        # the unexpected row shows where it is currently registered (bin_a)
        self.assertEqual(item_unexpected_b.conflict_level, "info")
        self.assertIn(self.bin_a.bin_identifier, item_unexpected_b.conflict)

    def test_no_conflict_when_isolated(self):
        annotate_conflicts([self.item_missing])
        self.assertEqual(self.item_missing.conflict, "")
        self.assertEqual(self.item_missing.conflict_level, "")

    # -- missing items accounted for elsewhere cannot be marked lost ----

    def _scan_missing_code_as_unexpected_in_bin_b(self):
        take_b = StockTake.objects.create(
            storage_bin=self.bin_b, performed_by=self.user
        )
        return StockTakeItem.objects.create(
            stock_take=take_b,
            stock=self.stock_missing,
            code=self.stock_missing.code,
            status=UNEXPECTED,
        )

    def test_missing_lost_blocked_when_elsewhere(self):
        self._scan_missing_code_as_unexpected_in_bin_b()
        response = self._post(self.item_missing, action="lost", reason="x")
        self.assertEqual(response.status_code, 302)
        self.item_missing.refresh_from_db()
        self.assertFalse(self.item_missing.resolved)

    def test_acknowledge_missing_when_elsewhere(self):
        self._scan_missing_code_as_unexpected_in_bin_b()
        response = self._post(
            self.item_missing, action="acknowledge", reason="it is in bin_b"
        )
        self.assertEqual(response.status_code, 302)
        self.item_missing.refresh_from_db()
        self.assertTrue(self.item_missing.acknowledged)

    def test_partial_missing_no_conflict_shows_lost(self):
        html = self._render_actions(self.item_missing)
        self.assertIn('value="lost"', html)
        self.assertIn("Mark lost", html)
        self.assertNotIn("Damaged", html)
        self.assertNotIn("Expired", html)
        self.assertNotIn("Acknowledge", html)

    def test_partial_missing_with_conflict_shows_acknowledge(self):
        self.item_missing.conflict = "Now registered in bin 000031."
        self.item_missing.conflict_level = "info"
        html = self._render_actions(self.item_missing)
        self.assertIn('value="acknowledge"', html)
        self.assertNotIn("Mark lost", html)

    # -- acknowledge (unresolvable unexpected items) -------------------

    def test_acknowledge_not_in_system(self):
        response = self._post(
            self.item_foreign, action="acknowledge", reason="foreign label"
        )
        self.assertEqual(response.status_code, 302)
        self.item_foreign.refresh_from_db()
        self.assertTrue(self.item_foreign.acknowledged)
        self.assertTrue(self.item_foreign.handled)
        self.assertEqual(self.item_foreign.acknowledged_by_id, self.user.id)
        self.assertEqual(self.item_foreign.acknowledged_note, "foreign label")

    def test_acknowledge_terminal_stock(self):
        # make the unexpected item's stock terminal (lost) -> not binnable
        apply_transaction(self.stock_unexpected, TXN_LOST, self.user, reason="x")
        self.stock_unexpected.refresh_from_db()
        self.assertTrue(self.stock_unexpected.is_terminal)
        response = self._post(
            self.item_unexpected, action="acknowledge", reason="dispensed in error"
        )
        self.assertEqual(response.status_code, 302)
        self.item_unexpected.refresh_from_db()
        self.assertTrue(self.item_unexpected.acknowledged)
        # the partial offers Acknowledge, not Add to bin, for terminal stock
        self.item_unexpected.acknowledged_datetime = None  # render the open state
        html = self._render_actions(self.item_unexpected)
        self.assertIn('value="acknowledge"', html)
        self.assertNotIn("Add to bin", html)

    def test_acknowledge_rejected_for_binnable_item(self):
        # stock_unexpected is stored (not terminal) -> must be added, not acknowledged
        response = self._post(
            self.item_unexpected, action="acknowledge", reason="x"
        )
        self.assertEqual(response.status_code, 302)
        self.item_unexpected.refresh_from_db()
        self.assertFalse(self.item_unexpected.acknowledged)

    def test_acknowledge_requires_note(self):
        response = self._post(self.item_foreign, action="acknowledge")
        self.assertEqual(response.status_code, 302)
        self.item_foreign.refresh_from_db()
        self.assertFalse(self.item_foreign.acknowledged)

    def test_unacknowledge_reopens(self):
        self._post(self.item_foreign, action="acknowledge", reason="foreign")
        self.item_foreign.refresh_from_db()
        self.assertTrue(self.item_foreign.acknowledged)
        self._post(self.item_foreign, action="unacknowledge")
        self.item_foreign.refresh_from_db()
        self.assertFalse(self.item_foreign.acknowledged)

    def test_partial_acknowledged_shows_badge(self):
        self._post(self.item_foreign, action="acknowledge", reason="foreign label")
        self.item_foreign.refresh_from_db()
        html = self._render_actions(self.item_foreign)
        self.assertIn("Acknowledged", html)
        self.assertIn("foreign label", html)
        self.assertIn('value="unacknowledge"', html)
