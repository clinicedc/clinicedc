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

    def test_resolve_unexpected_move_to_bin(self):
        response = self._post(
            self.item_unexpected, action="move_to_bin", reason="found in wrong bin"
        )
        self.assertEqual(response.status_code, 302)
        self.item_unexpected.refresh_from_db()
        self.assertTrue(self.item_unexpected.resolved)
        self.assertEqual(
            self.item_unexpected.stock_transaction.transaction_type, TXN_BIN_MOVED
        )
        # StorageBinItem for the stock now points at bin_a (the take's bin).
        sbi = StorageBinItem.objects.get(stock=self.stock_unexpected)
        self.assertEqual(sbi.storage_bin_id, self.bin_a.pk)

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

    def test_partial_open_missing_shows_status_form(self):
        html = self._render_actions(self.item_missing)
        self.assertIn('name="action"', html)
        for value in ("lost", "damaged", "expired"):
            self.assertIn(value, html)
        self.assertIn('name="reason"', html)
        self.assertIn("/next/", html)

    def test_partial_open_unexpected_shows_move_form(self):
        html = self._render_actions(self.item_unexpected)
        self.assertIn("move_to_bin", html)
        self.assertIn("Move to this bin", html)
        self.assertIn('name="reason"', html)

    def test_partial_not_in_system_shows_no_form(self):
        html = self._render_actions(self.item_foreign)
        self.assertNotIn("<form", html)
        self.assertIn("Not in system", html)

    def test_partial_resolved_shows_badge_and_link(self):
        self._post(self.item_missing, action="lost", reason="not on shelf")
        self.item_missing.refresh_from_db()
        html = self._render_actions(self.item_missing)
        self.assertIn("Resolved", html)
        self.assertNotIn("<form", html)
        # links to the resolving transaction in admin
        txn_url = reverse(
            "edc_pharmacy_admin:edc_pharmacy_stocktransaction_change",
            args=[self.item_missing.stock_transaction.pk],
        )
        self.assertIn(txn_url, html)
