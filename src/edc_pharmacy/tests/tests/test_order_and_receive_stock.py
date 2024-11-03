from secrets import choice

from dateutil.relativedelta import relativedelta
from django.contrib.sites.models import Site
from django.db.models import Count, Sum
from django.test import TestCase, tag
from edc_consent import site_consents
from edc_constants.constants import COMPLETE, FEMALE, MALE
from edc_list_data import site_list_data
from edc_randomization.constants import ACTIVE, PLACEBO
from edc_randomization.models import RandomizationList
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow
from sequences import get_next_value

from ...exceptions import InsufficientStockError
from ...models import (
    Assignment,
    Container,
    ContainerType,
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
    Units,
)
from ...models.stock import ContainerUnits, Request, RequestItem
from ...utils import process_request, repackage_stock
from ..consents import consent_v1


class TestOrderReceive(TestCase):
    def setUp(self):
        site_list_data.initialize()
        site_list_data.autodiscover()
        site_consents.registry = {}
        site_consents.loaded = False
        site_consents.register(consent_v1)

        self.medication = Medication.objects.create(
            name="METFORMIN",
        )

        self.formulation = Formulation.objects.create(
            medication=self.medication,
            strength=500,
            units=Units.objects.get(name="mg"),
            route=Route.objects.get(display_name="Oral"),
            formulation_type=FormulationType.objects.get(display_name__iexact="Tablet"),
        )
        self.assignment_active = Assignment.objects.create(name=ACTIVE)
        self.assignment_placebo = Assignment.objects.create(name=PLACEBO)
        self.lot_active = Lot.objects.create(
            lot_no="1234",
            assignment=self.assignment_active,
            expiration_date=get_utcnow() + relativedelta(years=1),
            formulation=self.formulation,
        )
        self.lot_placebo = Lot.objects.create(
            lot_no="4321",
            assignment=self.assignment_placebo,
            expiration_date=get_utcnow() + relativedelta(years=1),
            formulation=self.formulation,
        )
        self.location = Location.objects.create(name="central_pharmacy")
        self.location_amana = Location.objects.create(name="amana_pharmacy")
        self.product_active, self.product_placebo = self.make_products()

    def make_products(self):
        product_active = Product.objects.create(
            formulation=self.formulation,
            assignment=self.assignment_active,
        )
        product_placebo = Product.objects.create(
            formulation=self.formulation,
            assignment=self.assignment_placebo,
        )
        return product_active, product_placebo

    def make_order(self, container, qty: int | None = None):
        qty = qty or 100
        # product_active, product_placebo = self.make_products()
        order = Order.objects.create(order_datetime=get_utcnow())
        for i in range(0, 10):
            OrderItem.objects.create(
                order=order,
                product=self.product_active,
                qty=qty,
                container=container,
            )
        for i in range(10, 20):
            OrderItem.objects.create(
                order=order,
                product=self.product_placebo,
                qty=qty,
                container=container,
            )
        order.refresh_from_db()
        return order

    # def test_make_product(self):
    #     self.make_products()

    def test_make_order(self):
        """Test creating an order.

        1. Create products
        2. Create a new order
        3. Add order items to the order for the products
        """
        container_units, _ = ContainerUnits.objects.get_or_create(
            name="tablet", plural_name="tablets"
        )
        container_type, _ = ContainerType.objects.get_or_create(name="tablet")
        container = Container.objects.create(
            container_type=container_type,
            qty=1,
            units=container_units,
            may_order_as=True,
        )
        order = self.make_order(container)
        self.assertEqual(OrderItem.objects.all().count(), 20)
        self.assertEqual(order.item_count, 20)

    def test_receive_ordered_items(self):
        container_units, _ = ContainerUnits.objects.get_or_create(
            name="tablet", plural_name="tablets"
        )
        container_type, _ = ContainerType.objects.get_or_create(name="tablet")
        container = Container.objects.create(
            container_type=container_type,
            qty=1,
            units=container_units,
            may_order_as=True,
            may_receive_as=True,
        )
        order = self.make_order(container)
        receive = Receive.objects.create(order=order, location=self.location)
        order_items = order.orderitem_set.all()
        for order_item in order_items:
            obj = ReceiveItem.objects.create(
                receive=receive, order_item=order_item, qty=100, container=container
            )
            # assert container qty received
            self.assertEqual(obj.unit_qty, 100)

        # assert updates order_item.qty_received
        sums = OrderItem.objects.filter(order=order).aggregate(
            unit_qty=Sum("unit_qty"),
            unit_qty_received=Sum("unit_qty_received"),
        )
        self.assertEqual(sums["unit_qty"], 2000)
        self.assertEqual(sums["unit_qty_received"], 2000)

        # assert updates order_item.status
        for order_item in order_items:
            self.assertEqual(order_item.status, COMPLETE)

        # assert updates order.status
        order.refresh_from_db()
        self.assertEqual(order.status, COMPLETE)

        # assert added to stock
        self.assertEqual(
            Stock.objects.filter(receive_item__receive=receive).aggregate(
                qty_in=Sum("qty_in")
            )["qty_in"],
            2000,
        )
        for receive_item in ReceiveItem.objects.filter(receive=receive):
            self.assertTrue(receive_item.added_to_stock)

    def test_receive_ordered_items2(self):
        """Test receive where order product unit (e.g. Tablet) is not
        the same as received product unit (Bottle of 100 tablets).

        That is, we ordered 2000 tablets and received 20 bottles
        of 100 tablets
        """
        # order 2000 tablets
        container_units, _ = ContainerUnits.objects.get_or_create(
            name="tablet", plural_name="tablets"
        )
        container_type, _ = ContainerType.objects.get_or_create(name="tablet")
        container_2000 = Container.objects.create(
            container_type=container_type,
            qty=1,
            units=container_units,
            may_order_as=True,
        )
        order = self.make_order(container_2000)

        # receive 20 bottles or 100
        container_type, _ = ContainerType.objects.get_or_create(name="bottle")
        container_20 = Container.objects.create(
            container_type=container_type,
            qty=100,
            units=container_units,
            may_receive_as=True,
        )

        receive = Receive.objects.create(order=order, location=self.location)
        order_items = order.orderitem_set.all()
        for order_item in order_items:
            ReceiveItem.objects.create(
                receive=receive, order_item=order_item, qty=1, container=container_20
            )

        # assert updates order_item.qty_received
        sums = OrderItem.objects.filter(order=order).aggregate(
            unit_qty=Sum("unit_qty"), unit_qty_received=Sum("unit_qty_received")
        )
        self.assertEqual(sums["unit_qty"], 2000)
        self.assertEqual(sums["unit_qty_received"], 2000)

        # assert updates order_item.status
        for order_item in order_items:
            self.assertEqual(order_item.status, COMPLETE)

        # assert updates order.status
        order.refresh_from_db()
        self.assertEqual(order.status, COMPLETE)

        # assert added to stock
        self.assertEqual(
            Stock.objects.filter(receive_item__receive=receive).aggregate(
                qty_in=Sum("qty_in")
            )["qty_in"],
            20,
        )
        self.assertEqual(
            Stock.objects.filter(receive_item__receive=receive).aggregate(
                unit_qty_in=Sum("unit_qty_in")
            )["unit_qty_in"],
            2000,
        )
        for receive_item in ReceiveItem.objects.filter(receive=receive):
            self.assertTrue(receive_item.added_to_stock)

    def order_and_receive(self):
        # product_active, product_placebo = self.make_products()
        container_units, _ = ContainerUnits.objects.get_or_create(
            name="tablet", plural_name="tablets"
        )
        container_type, _ = ContainerType.objects.get_or_create(name="tablet")
        container = Container.objects.create(
            container_type=container_type,
            qty=1,
            units=container_units,
            may_order_as=True,
        )
        order = Order.objects.create(order_datetime=get_utcnow())
        OrderItem.objects.create(
            order=order,
            product=self.product_active,
            qty=50000,
            container=container,
        )
        OrderItem.objects.create(
            order=order,
            product=self.product_placebo,
            qty=50000,
            container=container,
        )
        order.refresh_from_db()

        container_type, _ = ContainerType.objects.get_or_create(name="bottle")
        container_bulk = Container.objects.create(
            container_type=container_type,
            qty=5000,
            units=container_units,
            may_receive_as=True,
        )

        receive = Receive.objects.create(order=order, location=self.location)
        order_items = order.orderitem_set.all()
        for order_item in order_items:
            ReceiveItem.objects.create(
                receive=receive, order_item=order_item, qty=10, container=container_bulk
            )

    def test_delete_receive_item(self):
        # confirm deleting stock, resave received items recreates
        self.order_and_receive()
        Stock.objects.all().delete()
        for obj in ReceiveItem.objects.all():
            self.assertFalse(obj.added_to_stock)
        for obj in ReceiveItem.objects.all():
            obj.save()
        self.assertEqual(Stock.objects.all().count(), 2)

        # confirm deleting stock & received items resets unit_qty_received on order items
        Stock.objects.all().delete()
        ReceiveItem.objects.all().delete()
        for order_item in OrderItem.objects.all():
            self.assertEqual(0, order_item.unit_qty_received)

    @tag("1")
    def test_repackage(self):
        """Test repackage two bottles of 50000 into
        bottles of 128.
        """
        # create order of 50000 for each arm
        self.order_and_receive()
        container_units, _ = ContainerUnits.objects.get_or_create(
            name="tablet", plural_name="tablets"
        )
        container_type, _ = ContainerType.objects.get_or_create(name="bottle")
        container_5000, _ = Container.objects.get_or_create(
            qty=5000, container_type=container_type
        )
        container_128 = Container.objects.create(
            container_type=container_type, qty=128, units=container_units
        )

        # we have two bottles of 5000 tablets
        unit_qty_in = Stock.objects.filter(container=container_5000).aggregate(
            unit_qty_in=Sum("unit_qty_in")
        )["unit_qty_in"]
        unit_qty_out = Stock.objects.filter(container=container_5000).aggregate(
            unit_qty_out=Sum("unit_qty_out")
        )["unit_qty_out"]
        unit_qty = unit_qty_in - unit_qty_out
        self.assertEqual(unit_qty, 100000)

        for stock in Stock.objects.filter(container=container_5000):
            for i in range(0, 401):
                try:
                    repackage_stock(stock, container_128)
                except InsufficientStockError:
                    break

        # we create bottles of 128 from the two bottles of 5000 tablets
        # the total number of tablets remains the same
        unit_qty_in = Stock.objects.all().aggregate(unit_qty_in=Sum("unit_qty_in"))[
            "unit_qty_in"
        ]
        unit_qty_out = Stock.objects.all().aggregate(unit_qty_out=Sum("unit_qty_out"))[
            "unit_qty_out"
        ]
        unit_qty = unit_qty_in - unit_qty_out
        self.assertEqual(unit_qty, 100000)

        # repackaged 99840 tablets into bottles of 128
        unit_qty_in = Stock.objects.filter(container=container_128).aggregate(
            unit_qty_in=Sum("unit_qty_in")
        )["unit_qty_in"]
        unit_qty_out = Stock.objects.filter(container=container_128).aggregate(
            unit_qty_out=Sum("unit_qty_out")
        )["unit_qty_out"]
        self.assertEqual(unit_qty_in - unit_qty_out, 99840)

        # 160 tablets leftover in the two bottles with capacity of 5000
        unit_qty_in = Stock.objects.filter(container=container_5000).aggregate(
            unit_qty_in=Sum("unit_qty_in")
        )["unit_qty_in"]
        unit_qty_out = Stock.objects.filter(container=container_5000).aggregate(
            unit_qty_out=Sum("unit_qty_out")
        )["unit_qty_out"]
        unit_qty = unit_qty_in - unit_qty_out
        self.assertEqual(unit_qty, 160)

    def make_randomized_subject(self, site: Site, subject_count: int):
        subjects = {}
        for i in range(0, subject_count):
            subjects.update({f"S{i:4d}": choice([self.product_placebo, self.product_active])})
        for subject_identifier, product in subjects.items():
            RegisteredSubject.objects.create(
                subject_identifier=subject_identifier,
                gender=choice([MALE, FEMALE]),
                randomization_list_model="edc_randomization.randomizationlist",
            )
            RandomizationList.objects.create(
                sid=get_next_value(sequence_name=RandomizationList._meta.label_lower),
                subject_identifier=subject_identifier,
                assignment=product.assignment.name,
                allocated_site=site,
                site_name=site.name,
                allocated=True,
                allocated_datetime=get_utcnow(),
            )
        return subjects

    def test_request_stock(self):
        self.order_and_receive()
        site_obj = Site.objects.create(id=10, name="Amana")

        subjects = self.make_randomized_subject(site_obj, 5)
        active_subjects = {k: v for k, v in subjects.items() if v == self.product_active}
        placebo_subjects = {k: v for k, v in subjects.items() if v == self.product_placebo}

        # repackage from bulk to generic bottle
        container_type, _ = ContainerType.objects.get_or_create(name="bottle")
        container_units, _ = ContainerUnits.objects.get_or_create(
            name="tablet", plural_name="tablets"
        )
        container_bulk = Container.objects.get(
            container_type=container_type, qty=5000, units=container_units
        )
        central_location = Location.objects.get(name="central_pharmacy")
        container_128 = Container.objects.create(
            container_type=container_type, qty=128, units=container_units
        )

        groupby = (
            Stock.objects.values("container__name")
            .filter(location=central_location, container=container_bulk)
            .annotate(items=Count("container"))
        )
        self.assertEqual(len(groupby), 1)
        self.assertEqual(groupby.get(container__name=container_bulk.name)["items"], 2)

        for _, product in subjects.items():
            stock = Stock.objects.get(
                location=central_location,
                container=container_bulk,
                product=product,
            )
            repackage_stock(stock, container_128)

        groupby = (
            Stock.objects.values("container__name")
            .filter(location=central_location)
            .annotate(items=Count("container"))
        )
        self.assertEqual(len(groupby), 2)
        self.assertEqual(groupby.get(container__name=container_128.name)["items"], 5)
        self.assertEqual(
            Stock.objects.filter(
                container__name=container_128.name, product=self.product_active
            ).count(),
            len(active_subjects),
        )
        self.assertEqual(
            Stock.objects.filter(
                container__name=container_128.name, product=self.product_placebo
            ).count(),
            len(placebo_subjects),
        )

        # create stock request
        container_128s = Container.objects.create(
            container_type=container_type,
            qty=128,
            units=container_units,
            may_request_as=True,
        )
        location = Location.objects.get(name="amana_pharmacy")
        request = Request.objects.create(
            location=location,
            container=container_128s,
            formulation=self.product_active.formulation,
            default_qty=1,
        )
        for subject_identifier, _ in subjects.items():
            RequestItem.objects.create(request=request, subject_identifier=subject_identifier)
        self.assertEqual(request.item_count, 5)

        # A. process request
        # 1. repackage from bulk to generic bottle
        # 2. repackage

        process_request(
            request, source_location=central_location, source_container=container_128
        )

        # **********************

        self.assertEqual(
            RequestItem.objects.filter(subject_identifier__in=active_subjects).count(),
            len(active_subjects),
        )
        self.assertEqual(
            Stock.objects.filter(
                request_item__in=RequestItem.objects.filter(
                    subject_identifier__in=active_subjects
                )
            ).count(),
            len(active_subjects),
        )

        locations = (
            Stock.objects.values("location__name")
            .annotate(location_count=Count("location__name"))
            .order_by("location__name")
        )
        self.assertEqual(locations.get(location__name="central_pharmacy")["location_count"], 7)
        self.assertEqual(locations.get(location__name="amana_pharmacy")["location_count"], 5)

    def test_allocate_to_subject(self):
        self.order_and_receive()
        container_units, _ = ContainerUnits.objects.get_or_create(
            name="tablet", plural_name="tablets"
        )
        container_type, _ = ContainerType.objects.get_or_create(name="bottle")
        container = Container.objects.create(
            container_type=container_type, qty=128, units=container_units
        )

        # pack 5 bottles or 128
        for index, stock in enumerate(Stock.objects.all()):
            for i in range(0, 5):
                repackage_stock(stock, container)
            break

        for subject_identifier in [f"SUBJECT{x}" for x in range(0, 5)]:
            # allocated_to_subject(subject_identifier, container, 3)
            pass
