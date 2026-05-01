"""Tests for the stock-return workflow.

Lifecycle under test:
  TXN_RETURN_REQUESTED
  TXN_RETURN_DISPATCHED
  TXN_RETURN_RECEIVED
  TXN_RETURN_DISPOSITION_REPOOLED / _QUARANTINED / _DESTROYED
"""

import uuid as _uuid
from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.action_items import register_actions
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.sites import all_sites
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings, tag
from django.utils import timezone

from edc_consent import site_consents
from edc_facility.import_holidays import import_holidays
from edc_pharmacy.constants import (
    CENTRAL_LOCATION,
    TXN_RETURN_DISPATCHED,
    TXN_RETURN_DISPOSITION_DESTROYED,
    TXN_RETURN_DISPOSITION_REPOOLED,
    TXN_RETURN_RECEIVED,
    TXN_RETURN_REQUESTED,
    TXN_STORED,
)
from edc_pharmacy.exceptions import InvalidTransitionError, ReturnError
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
    ReturnItem,
    ReturnRequest,
    Route,
    Stock,
    StockTransaction,
    StorageBin,
    Units,
)
from edc_pharmacy.transaction_log import apply_delta_context, apply_transaction
from edc_pharmacy.utils import (
    confirm_stock,
    dispatch_return,
    disposition_return,
    receive_return,
    request_stock_return,
)
from edc_randomization.constants import ACTIVE
from edc_sites.site import sites
from edc_sites.utils import add_or_update_django_sites
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

utc_tz = ZoneInfo("UTC")

User = get_user_model()


@tag("pharmacy_return")
@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=utc_tz))
@override_settings(SITE_ID=10)
class TestReturn(TestCase):
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

        self.actor, _ = User.objects.get_or_create(username=self.username)
        self.location_central, _ = Location.objects.get_or_create(
            name=CENTRAL_LOCATION, defaults={"display_name": "Return Test Central"}
        )
        self.location_site, _ = Location.objects.get_or_create(
            name="return_test_site", defaults={"display_name": "Return Test Site"}
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
        container_type_tablet, _ = ContainerType.objects.get_or_create(name="tablet_rtn")
        container_type_bottle, _ = ContainerType.objects.get_or_create(name="bottle_rtn")
        # Order container (must have may_order_as=True)
        container_order = Container.objects.create(
            name="rtn_tablet",
            display_name="Return Test Tablet",
            container_type=container_type_tablet,
            unit_qty_default=1,
            units=container_units,
            may_order_as=True,
        )
        # Receive container (must have may_receive_as=True)
        self.container = Container.objects.create(
            name="rtn_bottle_100",
            display_name="Return Test Bottle of 100",
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
        self.receive_item = ReceiveItem.objects.create(
            receive=receive,
            order_item=order_item,
            item_qty_received=3,
            container_unit_qty=self.container.unit_qty_default,
            container=self.container,
            lot=lot,
        )

        # Confirm all stock at central (sets confirmed=True, qty_in, unit_qty_in).
        codes = list(Stock.objects.values_list("code", flat=True))
        confirm_stock(
            receive,
            codes,
            fk_attr="receive_item__receive",
            user_created="aroy",
            actor=self.user,
        )

        self.stock_codes = list(Stock.objects.values_list("code", flat=True))
        self.storage_bin = StorageBin.objects.create(
            container=self.container,
            location=self.location_site,
        )

        # Drive stock to stored_at_location=True at site using apply_transaction.
        for stock in Stock.objects.all():
            # Simulate in-transit arrival at site by overriding location directly
            # (bypassing guarded fields via apply_delta_context for location move).
            with apply_delta_context():
                stock.location = self.location_site
                stock.save(update_fields=["location"])
            apply_transaction(stock, TXN_STORED, self.actor, storage_bin=self.storage_bin)

    def _get_stock(self, code: str) -> Stock:
        return Stock.objects.get(code=code)

    def test_return_requested(self):
        """TXN_RETURN_REQUESTED sets return_requested=True."""
        stock = Stock.objects.first()
        self.assertFalse(stock.return_requested)

        requested, skipped = request_stock_return(
            [stock.code], self.actor, reason="test request"
        )
        self.assertEqual(requested, [stock.code])
        self.assertEqual(skipped, [])

        stock.refresh_from_db()
        self.assertTrue(stock.return_requested)
        self.assertTrue(
            StockTransaction.objects.filter(
                stock=stock, transaction_type=TXN_RETURN_REQUESTED
            ).exists()
        )

    def test_return_requested_idempotent(self):
        """Second TXN_RETURN_REQUESTED raises InvalidTransitionError."""
        stock = Stock.objects.first()
        apply_transaction(stock, TXN_RETURN_REQUESTED, self.actor)

        with self.assertRaises(InvalidTransitionError):
            apply_transaction(stock, TXN_RETURN_REQUESTED, self.actor)

    def test_return_dispatched(self):
        """TXN_RETURN_DISPATCHED clears return_requested,
        sets in_transit, creates ReturnItem.
        """
        stock = Stock.objects.first()
        apply_transaction(stock, TXN_RETURN_REQUESTED, self.actor)
        stock.refresh_from_db()

        return_request = ReturnRequest.objects.create(
            from_location=self.location_site,
            to_location=self.location_central,
            item_count=1,
        )
        dispatched, skipped = dispatch_return(return_request, [stock.code], self.actor)
        self.assertEqual(dispatched, [stock.code])
        self.assertEqual(skipped, [])

        stock.refresh_from_db()
        self.assertFalse(stock.return_requested)
        self.assertTrue(stock.in_transit)
        self.assertFalse(stock.stored_at_location)
        self.assertEqual(stock.location, self.location_central)
        self.assertTrue(ReturnItem.objects.filter(stock=stock).exists())

    def test_return_dispatched_auto_requests(self):
        """dispatch_return auto-applies TXN_RETURN_REQUESTED when not already set.

        The view scans codes in a single step, so pre-calling
        request_stock_return() is not required.
        """
        stock = Stock.objects.first()
        # Do NOT pre-call TXN_RETURN_REQUESTED — dispatch handles it.
        return_request = ReturnRequest.objects.create(
            from_location=self.location_site,
            to_location=self.location_central,
            item_count=1,
        )
        dispatched, skipped = dispatch_return(return_request, [stock.code], self.actor)
        self.assertEqual(dispatched, [stock.code])
        self.assertEqual(skipped, [])
        stock.refresh_from_db()
        self.assertTrue(stock.in_transit)

    def test_return_dispatched_skips_stock_not_stored_at_location(self):
        """dispatch_return skips stock that is not in a bin at the site."""
        stock = Stock.objects.first()
        # Force stored_at_location=False via update() to bypass the guarded-field
        # check in save() — this is deliberate test setup, not production code.
        Stock.objects.filter(pk=stock.pk).update(stored_at_location=False)
        stock.refresh_from_db()
        return_request = ReturnRequest.objects.create(
            from_location=self.location_site,
            to_location=self.location_central,
            item_count=1,
        )
        dispatched, skipped = dispatch_return(return_request, [stock.code], self.actor)
        self.assertEqual(dispatched, [])
        self.assertEqual(len(skipped), 1)
        self.assertIn(stock.code, skipped[0])

    def test_return_received(self):
        """TXN_RETURN_RECEIVED clears in_transit at central."""
        stock = Stock.objects.first()
        return_request = ReturnRequest.objects.create(
            from_location=self.location_site,
            to_location=self.location_central,
            item_count=1,
        )
        dispatch_return(return_request, [stock.code], self.actor)
        stock.refresh_from_db()
        self.assertTrue(stock.in_transit)

        received, skipped = receive_return(return_request, [stock.code], self.actor)
        self.assertEqual(received, [stock.code])
        self.assertEqual(skipped, [])

        stock.refresh_from_db()
        self.assertFalse(stock.in_transit)

    def test_disposition_repooled(self):
        """TXN_RETURN_DISPOSITION_REPOOLED clears quarantined."""
        stock = Stock.objects.first()
        apply_transaction(stock, TXN_RETURN_REQUESTED, self.actor)
        return_request = ReturnRequest.objects.create(
            from_location=self.location_site,
            to_location=self.location_central,
            item_count=1,
        )
        dispatch_return(return_request, [stock.code], self.actor)
        receive_return(return_request, [stock.code], self.actor)

        processed, skipped = disposition_return(
            [stock.code], self.actor, disposition="repooled"
        )
        self.assertEqual(processed, [stock.code])
        self.assertEqual(skipped, [])

        stock.refresh_from_db()
        self.assertFalse(stock.quarantined)
        self.assertTrue(
            StockTransaction.objects.filter(
                stock=stock, transaction_type=TXN_RETURN_DISPOSITION_REPOOLED
            ).exists()
        )

    def test_disposition_quarantined(self):
        """TXN_RETURN_DISPOSITION_QUARANTINED sets quarantined=True."""
        stock = Stock.objects.first()
        apply_transaction(stock, TXN_RETURN_REQUESTED, self.actor)
        return_request = ReturnRequest.objects.create(
            from_location=self.location_site,
            to_location=self.location_central,
            item_count=1,
        )
        dispatch_return(return_request, [stock.code], self.actor)
        receive_return(return_request, [stock.code], self.actor)

        processed, _ = disposition_return([stock.code], self.actor, disposition="quarantined")
        self.assertEqual(processed, [stock.code])

        stock.refresh_from_db()
        self.assertTrue(stock.quarantined)

    def test_disposition_destroyed(self):
        """TXN_RETURN_DISPOSITION_DESTROYED sets destroyed=True."""
        stock = Stock.objects.first()
        apply_transaction(stock, TXN_RETURN_REQUESTED, self.actor)
        return_request = ReturnRequest.objects.create(
            from_location=self.location_site,
            to_location=self.location_central,
            item_count=1,
        )
        dispatch_return(return_request, [stock.code], self.actor)
        receive_return(return_request, [stock.code], self.actor)

        processed, _ = disposition_return([stock.code], self.actor, disposition="destroyed")
        self.assertEqual(processed, [stock.code])

        stock.refresh_from_db()
        self.assertTrue(stock.destroyed)

    def test_full_lifecycle_transaction_log(self):
        """Full return lifecycle produces exactly the expected TXN types."""
        stock = Stock.objects.first()
        apply_transaction(stock, TXN_RETURN_REQUESTED, self.actor)
        return_request = ReturnRequest.objects.create(
            from_location=self.location_site,
            to_location=self.location_central,
            item_count=1,
        )
        dispatch_return(return_request, [stock.code], self.actor)
        receive_return(return_request, [stock.code], self.actor)
        disposition_return([stock.code], self.actor, disposition="destroyed")

        txn_types = list(
            StockTransaction.objects.filter(stock=stock)
            .order_by("transaction_datetime", "created")
            .values_list("transaction_type", flat=True)
        )
        self.assertIn(TXN_STORED, txn_types)
        self.assertIn(TXN_RETURN_REQUESTED, txn_types)
        self.assertIn(TXN_RETURN_DISPATCHED, txn_types)
        self.assertIn(TXN_RETURN_RECEIVED, txn_types)
        self.assertIn(TXN_RETURN_DISPOSITION_DESTROYED, txn_types)

    def test_invalid_disposition(self):
        """disposition_return raises ReturnError for unknown disposition."""

        with self.assertRaises(ReturnError):
            disposition_return(["FAKE"], self.actor, disposition="recycled")

    def test_return_request_identifier_sequential(self):
        """ReturnRequest identifiers are auto-generated and sequential."""
        r1 = ReturnRequest.objects.create(
            from_location=self.location_site,
            to_location=self.location_central,
            item_count=1,
        )
        r2 = ReturnRequest.objects.create(
            from_location=self.location_site,
            to_location=self.location_central,
            item_count=1,
        )
        self.assertIsNotNone(r1.return_identifier)
        self.assertIsNotNone(r2.return_identifier)
        self.assertNotEqual(r1.return_identifier, r2.return_identifier)

    def test_return_request_same_location_raises(self):
        """ReturnRequest raises ReturnError if from_location == to_location."""
        with self.assertRaises(ReturnError):
            ReturnRequest.objects.create(
                from_location=self.location_central,
                to_location=self.location_central,
                item_count=1,
            )

    def test_allocation_held_until_disposition(self):
        """Allocation is NOT ended at dispatch or receipt — only at disposition.

        Stock remains allocated to the subject throughout the return journey.
        The allocation ends only when central sets a final disposition.
        """

        stock = Stock.objects.first()

        # Create a minimal allocation bypassing Allocation.save() guards
        # (stock_request_item, registered_subject not needed for this test).
        # Pre-assign pk so bulk_create works on MySQL (no RETURNING support).
        # Assignment must match stock.lot.assignment to pass verify_assignment_or_raise().
        alloc_pk = _uuid.uuid4()
        Allocation.objects.bulk_create(
            [
                Allocation(
                    id=alloc_pk,
                    stock=stock,
                    code=stock.code,
                    allocated_by="testactor",
                    allocation_identifier="test_alloc_001",
                    started_datetime=timezone.now(),
                    assignment=stock.lot.assignment,
                )
            ]
        )
        allocation = Allocation.objects.get(pk=alloc_pk)
        with apply_delta_context():
            stock.current_allocation = allocation
            stock.save(update_fields=["current_allocation"])

        return_request = ReturnRequest.objects.create(
            from_location=self.location_site,
            to_location=self.location_central,
            item_count=1,
        )

        # After dispatch: allocation still active.
        dispatch_return(return_request, [stock.code], self.actor)
        stock.refresh_from_db()
        self.assertIsNotNone(stock.current_allocation)
        self.assertEqual(stock.current_allocation.pk, allocation.pk)

        # After receipt: allocation still active.
        receive_return(return_request, [stock.code], self.actor)
        stock.refresh_from_db()
        self.assertIsNotNone(stock.current_allocation)
        self.assertEqual(stock.current_allocation.pk, allocation.pk)

        # After disposition (destroyed): allocation is ended.
        disposition_return([stock.code], self.actor, disposition="destroyed")
        stock.refresh_from_db()
        self.assertIsNone(stock.current_allocation)
        allocation.refresh_from_db()
        self.assertIsNotNone(allocation.ended_datetime)
        self.assertEqual(allocation.ended_reason, "destroyed")
