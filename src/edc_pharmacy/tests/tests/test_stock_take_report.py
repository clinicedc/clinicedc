"""Tests for the stock take discrepancy report helpers.

Covers the per-stock lookups and the site filter added to the discrepancy
report (clinicedc#127):

* ``utils.last_txn_abbr_by_stock`` — last ledger transaction code per stock.
* ``utils.subject_identifier_by_stock`` — recipient from the canonical
  Allocation table (robust where the Stock cache / sticky-pointer FK are empty,
  e.g. dispensed stock).
* ``views.stock_take_site_filter`` — site choices + ``?site=`` resolution.
* ``STOCK_TRANSACTION_ABBR`` — an abbreviation for every transaction type.
"""

import uuid
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
from django.test import RequestFactory, TestCase, override_settings, tag
from django.utils import timezone

from edc_consent import site_consents
from edc_facility.import_holidays import import_holidays
from edc_pharmacy.choices import STOCK_TRANSACTION_ABBR, STOCK_TRANSACTION_CHOICES
from edc_pharmacy.constants import CENTRAL_LOCATION, TXN_BIN_MOVED, TXN_STORED
from edc_pharmacy.models import (
    Allocation,
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
    StorageBin,
    Units,
)
from edc_pharmacy.transaction_log import apply_delta_context, apply_transaction
from edc_pharmacy.utils import (
    confirm_stock,
    last_txn_abbr_by_stock,
    subject_identifier_by_stock,
)
from edc_pharmacy.views.stock_take_site_filter import (
    get_selected_site_id,
    stock_take_site_choices,
)
from edc_randomization.constants import ACTIVE
from edc_sites.site import sites
from edc_sites.utils import add_or_update_django_sites
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

utc_tz = ZoneInfo("UTC")

User = get_user_model()


@tag("stock_take_report")
@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=utc_tz))
@override_settings(SITE_ID=10)
class TestStockTakeReport(TestCase):
    username = "aroy"
    site_id = 10

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

        self.bin_a = StorageBin.objects.create(
            container=self.container, location=self.location_site
        )
        self.bin_b = StorageBin.objects.create(
            container=self.container, location=self.location_site
        )

        # Drive all stock to stored_at_location=True at the site.
        stocks = list(Stock.objects.order_by("code"))
        self.stock_a, self.stock_b, self.stock_c = stocks
        for stock, storage_bin in (
            (self.stock_a, self.bin_a),
            (self.stock_b, self.bin_a),
            (self.stock_c, self.bin_b),
        ):
            with apply_delta_context():
                stock.location = self.location_site
                stock.save(update_fields=["location"])
            apply_transaction(stock, TXN_STORED, self.actor, storage_bin=storage_bin)

    # -- last_txn_abbr_by_stock ----------------------------------------

    def test_last_txn_abbr_for_stored_stock(self):
        result = last_txn_abbr_by_stock([self.stock_a.pk, self.stock_b.pk])
        self.assertEqual(result[self.stock_a.pk], "STR")
        self.assertEqual(result[self.stock_b.pk], "STR")

    def test_last_txn_abbr_reflects_most_recent(self):
        # Move stock_a to bin_b; the latest transaction is now BIN_MOVED -> MVD.
        apply_transaction(self.stock_a, TXN_BIN_MOVED, self.actor, storage_bin=self.bin_b)
        result = last_txn_abbr_by_stock([self.stock_a.pk])
        self.assertEqual(result[self.stock_a.pk], "MVD")

    def test_last_txn_abbr_skips_falsy_ids_and_empty(self):
        self.assertEqual(last_txn_abbr_by_stock([]), {})
        self.assertEqual(last_txn_abbr_by_stock([None]), {})

    def test_last_txn_abbr_omits_stock_without_ledger(self):
        # An id with no StockTransaction rows is absent from the map.
        unknown = uuid.uuid4()
        result = last_txn_abbr_by_stock([self.stock_a.pk, unknown])
        self.assertIn(self.stock_a.pk, result)
        self.assertNotIn(unknown, result)

    # -- subject_identifier_by_stock -----------------------------------

    @staticmethod
    def _new_allocation(stock, subject_identifier, *, code=None, allocated=None, ended=None):
        # bulk_create bypasses Allocation.save() (Rx / randomizer lookups), which
        # is unnecessary here — we only need the canonical subject_identifier row.
        # Set the pk explicitly: BaseUuidModel's pk isn't assigned at init, so
        # bulk_create would otherwise trip Django's returning-columns assertion.
        allocation = Allocation(
            stock=stock,
            code=code,
            subject_identifier=subject_identifier,
            allocation_datetime=allocated or timezone.now(),
            ended_datetime=ended,
        )
        allocation.pk = uuid.uuid4()
        return allocation

    def _allocate(self, stock, subject_identifier):
        Allocation.objects.bulk_create(
            [self._new_allocation(stock, subject_identifier, code=stock.code)]
        )

    def test_subject_from_allocation_table(self):
        self._allocate(self.stock_a, "105-40-0001-1")
        result = subject_identifier_by_stock([self.stock_a.pk])
        self.assertEqual(result[self.stock_a.pk], "105-40-0001-1")

    def test_subject_independent_of_stock_cache(self):
        # The Stock.subject_identifier cache and the Stock.allocation sticky FK
        # are both empty (as for dispensed stock), yet the recipient resolves
        # from the Allocation table. This is the clinicedc#127 regression.
        self._allocate(self.stock_a, "105-40-0009-9")
        self.stock_a.refresh_from_db()
        self.assertEqual(self.stock_a.subject_identifier, "")
        self.assertIsNone(self.stock_a.allocation_id)
        result = subject_identifier_by_stock([self.stock_a.pk])
        self.assertEqual(result[self.stock_a.pk], "105-40-0009-9")

    def test_subject_most_recent_allocation_wins(self):
        # Only one allocation may be active per stock, so the older one is ended
        # (the sticky-history case). The most recent allocation_datetime wins.
        now = timezone.now()
        Allocation.objects.bulk_create(
            [
                self._new_allocation(
                    self.stock_a, "OLD-SUBJECT", allocated=now, ended=now
                ),
                self._new_allocation(
                    self.stock_a, "NEW-SUBJECT", allocated=now + relativedelta(days=1)
                ),
            ]
        )
        result = subject_identifier_by_stock([self.stock_a.pk])
        self.assertEqual(result[self.stock_a.pk], "NEW-SUBJECT")

    def test_subject_unallocated_and_empty(self):
        self.assertEqual(subject_identifier_by_stock([self.stock_a.pk]), {})
        self.assertEqual(subject_identifier_by_stock([]), {})
        self.assertEqual(subject_identifier_by_stock([None]), {})

    # -- site filter ---------------------------------------------------

    def test_site_choices_lists_only_sites_with_bins(self):
        choices = stock_take_site_choices(StorageBin.objects.filter(in_use=True))
        self.assertEqual([choice.id for choice in choices], [self.site_id])
        # Display name comes from the edc_sites global, not the raw Site.name.
        self.assertEqual(choices[0].display_name, sites.get(self.site_id).description)

    def test_selected_site_id_valid(self):
        choices = stock_take_site_choices(StorageBin.objects.filter(in_use=True))
        request = RequestFactory().get("/", {"site": str(self.site_id)})
        self.assertEqual(get_selected_site_id(request, choices), self.site_id)

    def test_selected_site_id_defaults_and_rejects(self):
        choices = stock_take_site_choices(StorageBin.objects.filter(in_use=True))
        # No param -> All sites (None)
        self.assertIsNone(get_selected_site_id(RequestFactory().get("/"), choices))
        # Not an offered site -> None
        self.assertIsNone(
            get_selected_site_id(RequestFactory().get("/", {"site": "999"}), choices)
        )
        # Non-numeric -> None
        self.assertIsNone(
            get_selected_site_id(RequestFactory().get("/", {"site": "abc"}), choices)
        )

    # -- abbreviation map invariant ------------------------------------

    def test_every_transaction_type_has_an_abbreviation(self):
        missing = [
            txn_type
            for txn_type, _ in STOCK_TRANSACTION_CHOICES
            if txn_type not in STOCK_TRANSACTION_ABBR
        ]
        self.assertEqual(missing, [])

    def test_abbreviations_are_three_upper_letters(self):
        for abbr in STOCK_TRANSACTION_ABBR.values():
            self.assertEqual(len(abbr), 3, msg=abbr)
            self.assertTrue(abbr.isupper(), msg=abbr)
