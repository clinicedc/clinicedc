from secrets import choice

from dateutil.relativedelta import relativedelta
from django.contrib.sites.models import Site
from django.db.models import Sum
from django.test import TestCase
from edc_consent import site_consents
from edc_constants.constants import COMPLETE, FEMALE, MALE
from edc_list_data import site_list_data
from edc_randomization.constants import ACTIVE, PLACEBO
from edc_randomization.models import RandomizationList
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow
from sequences import get_next_value

from ...exceptions import RepackRequestError
from ...models import (
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
    RepackRequest,
    Route,
    Stock,
    Units,
)
from ...utils import confirm_stock, process_repack_request
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
        self.product_active, self.product_placebo = self.make_products()
        self.lot_active = Lot.objects.create(
            lot_no="1234",
            assignment=self.assignment_active,
            expiration_date=get_utcnow() + relativedelta(years=1),
            product=self.product_active,
        )
        self.lot_placebo = Lot.objects.create(
            lot_no="4321",
            assignment=self.assignment_placebo,
            expiration_date=get_utcnow() + relativedelta(years=1),
            product=self.product_placebo,
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

    def make_order(self, container, qty: int | None = None):
        qty = qty or 100
        # product_active, product_placebo = self.make_products()
        order = Order.objects.create(order_datetime=get_utcnow(), item_count=20)
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
        sums = OrderItem.objects.filter(order=order).aggregate(
            unit_qty=Sum("unit_qty"),
            unit_qty_received=Sum("unit_qty_received"),
        )
        self.assertEqual(sums["unit_qty"], 2000)
        self.assertEqual(sums["unit_qty_received"], None)

        for order_item in order_items:
            obj = ReceiveItem.objects.create(
                receive=receive,
                order_item=order_item,
                qty=100,
                container=container,
                lot=(
                    self.lot_active
                    if order_item.product.assignment.name == "active"
                    else self.lot_placebo
                ),
            )
            # assert container qty received
            self.assertEqual(obj.unit_qty, 100)

        # assert updates order_item.qty_received
        sums = OrderItem.objects.filter(order=order).aggregate(
            unit_qty=Sum("unit_qty"),
            unit_qty_received=Sum("unit_qty_received"),
        )
        self.assertEqual(sums["unit_qty"], 0)
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
                receive=receive,
                order_item=order_item,
                qty=1,
                container=container_20,
                lot=(
                    self.lot_active
                    if order_item.product.assignment.name == "active"
                    else self.lot_placebo
                ),
            )

        # assert updates order_item.qty_received
        sums = OrderItem.objects.filter(order=order).aggregate(
            unit_qty=Sum("unit_qty"), unit_qty_received=Sum("unit_qty_received")
        )
        self.assertEqual(sums["unit_qty"], 0)
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
                receive=receive,
                order_item=order_item,
                qty=10,
                container=container_bulk,
                lot=(
                    self.lot_active
                    if order_item.product.assignment.name == "active"
                    else self.lot_placebo
                ),
            )
        receive.save()
        return receive

    def test_delete_receive_item(self):
        # confirm deleting stock, resave received items recreates
        self.order_and_receive()
        Stock.objects.all().delete()
        for obj in ReceiveItem.objects.all():
            obj.save()
        # assert stock count is equal to receiveditem.qty *
        # receiveitem.count()
        self.assertEqual(
            Stock.objects.all().count(),
            int(ReceiveItem.objects.values("qty").aggregate(qty=Sum("qty")).get("qty")),
        )

        # confirm deleting stock & received items resets unit_qty_received on order items
        Stock.objects.all().delete()
        ReceiveItem.objects.all().delete()
        for order_item in OrderItem.objects.all():
            self.assertEqual(0, order_item.unit_qty_received)

    def get_container_5000(self) -> Container:
        container_units, _ = ContainerUnits.objects.get_or_create(
            name="tablet", plural_name="tablets"
        )
        container_type, _ = ContainerType.objects.get_or_create(name="bottle")
        container_5000, _ = Container.objects.get_or_create(
            qty=5000, container_type=container_type
        )
        return container_5000

    def get_container_128(self) -> Container:
        container_units, _ = ContainerUnits.objects.get_or_create(
            name="tablet", plural_name="tablets"
        )
        container_type, _ = ContainerType.objects.get_or_create(name="bottle")
        container_128, _ = Container.objects.get_or_create(
            qty=128, container_type=container_type
        )
        return container_128

    def test_repack(self):
        """Test repackage two bottles of 50000 into bottles of 128."""
        # create order of 50000 for each arm
        receive = self.order_and_receive()

        # assert created stock
        container_5000 = self.get_container_5000()
        container_128 = self.get_container_128()

        # assert
        self.assertEqual(Stock.objects.filter(container=container_5000).count(), 20)
        self.assertEqual(
            Stock.objects.values("container__name")
            .annotate(count=Sum("qty_in"))[0]
            .get("count"),
            20,
        )
        self.assertEqual(
            Stock.objects.values("container__name")
            .annotate(count=Sum("unit_qty_in"))[0]
            .get("count"),
            100000,
        )

        # assert raises if stock not confirmed
        stock = Stock.objects.filter(container=container_5000).first()
        with self.assertRaises(RepackRequestError) as cm:
            repack_request = RepackRequest.objects.create(
                from_stock=stock,
                container=container_128,
                requested_qty=39,
            )
        self.assertIn("Unconfirmed stock item", str(cm.exception))

        # confirm stock items
        for stock in Stock.objects.filter(container=container_5000):
            confirm_stock(receive, [stock.code], fk_attr="receive_item__receive")

        # REPACK REQUEST **********************************************
        for stock in Stock.objects.filter(container=container_5000):
            # create request
            repack_request = RepackRequest.objects.create(
                from_stock=stock,
                container=container_128,
                requested_qty=39,
            )
            # process
            process_repack_request(repack_request.pk, username=None)

        for repack_request in RepackRequest.objects.all():
            # assert unconfirmed stock instances (central)
            self.assertEqual(repack_request.stock_set.filter(confirmed=False).count(), 39)

        # scan in some or all labels to confirm stock (central)
        for repack_request in RepackRequest.objects.all():
            codes = [obj.code for obj in repack_request.stock_set.filter(confirmed=False)]
            confirmed, already_confirmed, invalid = confirm_stock(
                repack_request, codes, fk_attr="repack_request"
            )

            self.assertEqual(len(confirmed), 39)
            self.assertEqual(len(already_confirmed), 0)
            self.assertEqual(len(invalid), 0)

        for repack_request in RepackRequest.objects.all():
            codes = [
                f"{obj.code}blah" for obj in repack_request.stock_set.filter(confirmed=True)
            ]
            confirmed, already_confirmed, invalid = confirm_stock(
                repack_request, codes, fk_attr="repack_request"
            )

            self.assertEqual(len(confirmed), 0)
            self.assertEqual(len(already_confirmed), 0)
            self.assertEqual(len(invalid), 39)

        for repack_request in RepackRequest.objects.all():
            codes = [obj.code for obj in repack_request.stock_set.filter(confirmed=True)]
            confirmed, already_confirmed, invalid = confirm_stock(
                repack_request, codes, fk_attr="repack_request"
            )

            self.assertEqual(len(confirmed), 0)
            self.assertEqual(len(already_confirmed), 39)
            self.assertEqual(len(invalid), 0)

        for repack_request in RepackRequest.objects.all():
            # assert unconfirmed stock instances (central)
            self.assertEqual(repack_request.stock_set.filter(confirmed=False).count(), 0)
            # assert confirmed stock instances (central)
            self.assertEqual(repack_request.stock_set.filter(confirmed=True).count(), 39)

        # refer back to repack_request from stock
        self.assertEqual(Stock.objects.filter(repack_request__isnull=True).count(), 20)
        self.assertEqual(Stock.objects.filter(repack_request__isnull=False).count(), 39 * 20)

        # we create bottles of 128 from the two bottles of 50000 tablets
        # the total number of tablets remains the same
        unit_qty_in = Stock.objects.all().aggregate(unit_qty_in=Sum("unit_qty_in"))[
            "unit_qty_in"
        ]
        self.assertEqual(unit_qty_in, 199840)

        unit_qty_out = Stock.objects.all().aggregate(unit_qty_out=Sum("unit_qty_out"))[
            "unit_qty_out"
        ]
        self.assertEqual(unit_qty_out, 99840)

        # repackaged 99840 tablets into bottles of 128
        unit_qty_in = Stock.objects.filter(container=container_128).aggregate(
            unit_qty_in=Sum("unit_qty_in")
        )["unit_qty_in"]
        self.assertEqual(unit_qty_in, 99840)

        unit_qty_out = Stock.objects.filter(container=container_128).aggregate(
            unit_qty_out=Sum("unit_qty_out")
        )["unit_qty_out"]
        self.assertEqual(unit_qty_out, 0)

        # 160 tablets leftover in the two bottles with capacity of 50000
        unit_qty_in = Stock.objects.filter(container=container_5000).aggregate(
            unit_qty_in=Sum("unit_qty_in")
        )["unit_qty_in"]
        self.assertEqual(unit_qty_in, 100000)
        unit_qty_out = Stock.objects.filter(container=container_5000).aggregate(
            unit_qty_out=Sum("unit_qty_out")
        )["unit_qty_out"]
        self.assertEqual(unit_qty_out, 99840)
        self.assertEqual(unit_qty_in - unit_qty_out, 160)

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

    def test_allocate_to_subject(self):
        self.order_and_receive()
