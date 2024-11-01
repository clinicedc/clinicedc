from dateutil.relativedelta import relativedelta
from django.db.models import Count, Sum
from django.test import TestCase, tag
from edc_consent import site_consents
from edc_constants.constants import COMPLETE
from edc_list_data import site_list_data
from edc_randomization.constants import ACTIVE, PLACEBO
from edc_utils import get_utcnow

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
from ...models.stock import ContainerUnits
from ...utils import repackage_stock
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
        self.assignment_active = Assignment.objects.create(assignment=ACTIVE)
        self.assignment_placebo = Assignment.objects.create(assignment=PLACEBO)
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

    def make_order(self, container, unit_qty: int | None = None):
        unit_qty = unit_qty or 100
        product_active, product_placebo = self.make_products()
        order = Order.objects.create(order_datetime=get_utcnow())
        for i in range(0, 10):
            OrderItem.objects.create(
                order=order,
                product=product_active,
                unit_qty=unit_qty,
                container=container,
            )
        for i in range(10, 20):
            OrderItem.objects.create(
                order=order,
                product=product_placebo,
                unit_qty=unit_qty,
                container=container,
            )
        order.refresh_from_db()
        return order

    @tag("1")
    def test_make_product(self):
        self.make_products()

    @tag("1")
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
            container_type=container_type, container_qty=1, container_units=container_units
        )
        order = self.make_order(container)
        self.assertEqual(OrderItem.objects.all().count(), 20)
        order.refresh_from_db()
        self.assertEqual(order.unit_qty, 2000)
        self.assertEqual(order.container_qty, 2000)

    @tag("1")
    def test_receive_ordered_items(self):
        container_units, _ = ContainerUnits.objects.get_or_create(
            name="tablet", plural_name="tablets"
        )
        container_type, _ = ContainerType.objects.get_or_create(name="tablet")
        container = Container.objects.create(
            container_type=container_type, container_qty=1, container_units=container_units
        )
        order = self.make_order(container)
        receive = Receive.objects.create(order=order, location=self.location)
        order_items = order.orderitem_set.all()
        for order_item in order_items:
            obj = ReceiveItem.objects.create(
                receive=receive, order_item=order_item, unit_qty=100, container=container
            )
            # assert container qty received
            self.assertEqual(obj.container_qty, 100)

        # assert updates order_item.qty_received
        sums = OrderItem.objects.filter(order=order).aggregate(
            container_qty=Sum("container_qty"),
            container_qty_received=Sum("container_qty_received"),
        )
        self.assertEqual(sums["container_qty"], 2000)
        self.assertEqual(sums["container_qty_received"], 2000)

        # assert updates order_item.status
        for order_item in order_items:
            self.assertEqual(order_item.status, COMPLETE)

        # assert updates order.status
        order.refresh_from_db()
        self.assertEqual(order.status, COMPLETE)

        # assert added to stock
        self.assertEqual(
            Stock.objects.filter(receive_item__receive=receive).aggregate(
                unit_qty_in=Sum("unit_qty_in")
            )["unit_qty_in"],
            2000,
        )
        for receive_item in ReceiveItem.objects.filter(receive=receive):
            self.assertTrue(receive_item.added_to_stock)

    @tag("1")
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
        container = Container.objects.create(
            container_type=container_type, container_qty=1, container_units=container_units
        )
        order = self.make_order(container)

        # receive 20 bottles or 100
        container_type, _ = ContainerType.objects.get_or_create(name="bottle")
        container = Container.objects.create(
            container_type=container_type, container_qty=100, container_units=container_units
        )

        receive = Receive.objects.create(order=order, location=self.location)
        order_items = order.orderitem_set.all()
        for order_item in order_items:
            ReceiveItem.objects.create(
                receive=receive, order_item=order_item, unit_qty=1, container=container
            )

        # assert updates order_item.qty_received
        sums = OrderItem.objects.filter(order=order).aggregate(
            qty_ordered=Sum("container_qty"), qty_received=Sum("container_qty_received")
        )
        self.assertEqual(sums["qty_ordered"], 2000)
        self.assertEqual(sums["qty_received"], 2000)

        # assert updates order_item.status
        for order_item in order_items:
            self.assertEqual(order_item.status, COMPLETE)

        # assert updates order.status
        order.refresh_from_db()
        self.assertEqual(order.status, COMPLETE)

        # assert added to stock
        self.assertEqual(
            Stock.objects.filter(receive_item__receive=receive).aggregate(
                unit_qty_in=Sum("unit_qty_in")
            )["unit_qty_in"],
            20,
        )
        self.assertEqual(
            Stock.objects.filter(receive_item__receive=receive).aggregate(
                container_qty_in=Sum("container_qty_in")
            )["container_qty_in"],
            2000,
        )
        for receive_item in ReceiveItem.objects.filter(receive=receive):
            self.assertTrue(receive_item.added_to_stock)

    def order_and_receive(self):
        product_active, product_placebo = self.make_products()
        container_units, _ = ContainerUnits.objects.get_or_create(
            name="tablet", plural_name="tablets"
        )
        container_type, _ = ContainerType.objects.get_or_create(name="tablet")
        container = Container.objects.create(
            container_type=container_type, container_qty=1, container_units=container_units
        )
        order = Order.objects.create(order_datetime=get_utcnow())
        OrderItem.objects.create(
            order=order,
            product=product_active,
            unit_qty=50000,
            container=container,
        )
        OrderItem.objects.create(
            order=order,
            product=product_placebo,
            unit_qty=50000,
            container=container,
        )
        order.refresh_from_db()

        container_type, _ = ContainerType.objects.get_or_create(name="bottle")
        container = Container.objects.create(
            container_type=container_type, container_qty=5000, container_units=container_units
        )

        receive = Receive.objects.create(order=order, location=self.location)
        order_items = order.orderitem_set.all()
        for order_item in order_items:
            ReceiveItem.objects.create(
                receive=receive, order_item=order_item, unit_qty=10, container=container
            )

    @tag("1")
    def test_delete_receive_item(self):
        # confirm deleting stock, resave received items recreates
        self.order_and_receive()
        Stock.objects.all().delete()
        for obj in ReceiveItem.objects.all():
            self.assertFalse(obj.added_to_stock)
        for obj in ReceiveItem.objects.all():
            obj.save()
        self.assertEqual(Stock.objects.all().count(), 2)

        # confirm deleting stock & received items resets container_qty_received on order items
        Stock.objects.all().delete()
        ReceiveItem.objects.all().delete()
        for order_item in OrderItem.objects.all():
            self.assertEqual(0, order_item.container_qty_received)

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
        container = Container.objects.create(
            container_type=container_type, container_qty=128, container_units=container_units
        )
        for stock in Stock.objects.all():
            x = 0
            while x < 401:
                try:
                    repackage_stock(stock, container)
                except InsufficientStockError:
                    break
                # else:
                #     print(x, stock.container_qty_in, stock.container_qty_out)
                x += 1
        self.assertEqual(
            Stock.objects.all().aggregate(container_qty=Sum("container_qty"))["container_qty"],
            100000,
        )
        # repackaged 99840 tablets
        self.assertEqual(
            Stock.objects.filter(container__container_qty=128).aggregate(
                container_qty=Sum("container_qty")
            )["container_qty"],
            99840,
        )
        # 160 tablets leftover
        self.assertEqual(
            Stock.objects.filter(container__container_qty=5000).aggregate(
                container_qty=Sum("container_qty")
            )["container_qty"],
            160,
        )

    @tag("1")
    def test_transfer_stock(self):
        self.order_and_receive()
        container_units, _ = ContainerUnits.objects.get_or_create(
            name="tablet", plural_name="tablets"
        )
        container_type, _ = ContainerType.objects.get_or_create(name="bottle")
        container = Container.objects.create(
            container_type=container_type, container_qty=128, container_units=container_units
        )

        # pack 5 bottles or 128
        for index, stock in enumerate(Stock.objects.all()):
            for i in range(0, 5):
                repackage_stock(stock, container)
            break

        locations = (
            Stock.objects.values("location__name")
            .annotate(location_count=Count("location__name"))
            .order_by("location__name")
        )
        self.assertEqual(locations.get(location__name="central_pharmacy")["location_count"], 7)

        # set location to Amana
        Stock.objects.filter(container__container_qty=128).update(location=self.location_amana)

        locations = (
            Stock.objects.values("location__name")
            .annotate(location_count=Count("location__name"))
            .order_by("location__name")
        )
        self.assertEqual(locations.get(location__name="central_pharmacy")["location_count"], 2)
        self.assertEqual(locations.get(location__name="amana_pharmacy")["location_count"], 5)

    def test_allocate_to_subject(self):
        self.order_and_receive()
        container_units, _ = ContainerUnits.objects.get_or_create(
            name="tablet", plural_name="tablets"
        )
        container_type, _ = ContainerType.objects.get_or_create(name="bottle")
        container = Container.objects.create(
            container_type=container_type, container_qty=128, container_units=container_units
        )

        # pack 5 bottles or 128
        for index, stock in enumerate(Stock.objects.all()):
            for i in range(0, 5):
                repackage_stock(stock, container)
            break

        for subject_identifier in [f"SUBJECT{x}" for x in range(0, 5)]:
            # allocated_to_subject(subject_identifier, container, 3)
            pass
