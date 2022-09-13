from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag
from edc_list_data import site_list_data
from edc_utils import get_utcnow

from edc_pharmacy.exceptions import InsufficientQuantityError
from edc_pharmacy.models import (
    Box,
    ContainerType,
    Formulation,
    FormulationType,
    GenericContainer,
    Location,
    Medication,
    MedicationLot,
    PillBottle,
    Room,
    Route,
    Shelf,
    Units,
    get_location,
    get_room,
    get_shelf,
    repackage,
)


class TestPrescription(TestCase):
    def setUp(self):
        site_list_data.initialize()
        site_list_data.autodiscover()

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

    @tag("11")
    def test_build_location(self):

        location = Location.objects.create(name="LOCATION_ONE")
        room = Room.objects.create(name="ROOM_ONE", location=location)
        shelf = Shelf.objects.create(name="SHELF_ONE", room=room)
        box = Box.objects.create(name="BOX_ONE", shelf=shelf)
        container_type = ContainerType.objects.create(name="Bottle")
        for i in [1, 2, 3]:
            GenericContainer.objects.create(
                container_type=container_type, name=f"BOTTLE_{i}", box=box
            )

    @tag("11")
    def test_add_unpackaged_medicationitem(self):
        container_type = ContainerType.objects.create(name="bottle")
        medication_lot_one = MedicationLot.objects.create(
            lot_no="LOT1111111",
            formulation=self.formulation,
            expiration_date=get_utcnow() + relativedelta(years=1),
        )
        medication_lot_two = MedicationLot.objects.create(
            lot_no="LOT222222",
            expiration_date=get_utcnow() + relativedelta(years=1),
            formulation=self.formulation,
        )

        location = Location.objects.create(name="LOCATION_ONE")
        room = Room.objects.create(name="ROOM_ONE", location=location)
        shelf_one = Shelf.objects.create(name="SHELF_ONE", room=room)
        Shelf.objects.create(name="SHELF_TWO", room=room)
        Shelf.objects.create(name="SHELF_THREE", room=room)
        Shelf.objects.create(name="SHELF_FOUR", room=room)

        box = Box.objects.create(name="BOX_ONE", shelf=shelf_one)
        for i in [1, 2, 3, 4, 5, 6]:
            PillBottle.objects.create(
                container_type=container_type,
                name=f"BOTTLE_{i}",
                medication_lot=medication_lot_one,
                unit_qty=32,
                box=box,
            )
            PillBottle.objects.create(
                container_type=container_type,
                name=f"BOTTLE_{i + 10}",
                medication_lot=medication_lot_two,
                unit_qty=32,
                box=box,
            )
        for obj in PillBottle.objects.all():
            self.assertEqual(str(obj), "Metformin 500Mg Tablet Oral 32 count")

    @tag("11")
    def test_where_is_the_bottle(self):
        container_type = ContainerType.objects.create(name="bottle")
        medication_lot_one = MedicationLot.objects.create(
            lot_no="LOT1111111",
            formulation=self.formulation,
            expiration_date=get_utcnow() + relativedelta(years=1),
        )

        location = Location.objects.create(name="LOCATION_ONE")
        room = Room.objects.create(name="ROOM_ONE", location=location)
        shelf_one = Shelf.objects.create(name="SHELF_ONE", room=room)

        box = Box.objects.create(name="BOX_ONE", shelf=shelf_one)
        for i in [1, 2, 3, 4, 5, 6]:
            PillBottle.objects.create(
                container_type=container_type,
                name=f"BOTTLE_{i}",
                medication_lot=medication_lot_one,
                unit_qty=32,
                box=box,
            )
        pill_bottle = PillBottle.objects.get(name="BOTTLE_2")

        self.assertTrue(get_location(item=pill_bottle), location)
        self.assertTrue(get_room(item=pill_bottle), room)
        self.assertTrue(get_shelf(item=pill_bottle), shelf_one)

    @tag("11")
    def test_repack(self):
        container_type = ContainerType.objects.create(name="bottle")
        medication_lot_one = MedicationLot.objects.create(
            lot_no="LOT1111111",
            formulation=self.formulation,
            expiration_date=get_utcnow() + relativedelta(years=1),
        )

        location = Location.objects.create(name="LOCATION_ONE")
        room = Room.objects.create(name="ROOM_ONE", location=location)
        shelf_one = Shelf.objects.create(name="SHELF_ONE", room=room)
        shelf_two = Shelf.objects.create(name="SHELF_TWO", room=room)
        box_two = Box.objects.create(name="BOX_TWO", shelf=shelf_two)
        box_one = Box.objects.create(name="BOX_ONE", shelf=shelf_one)
        for i in [1, 2, 3, 4, 5, 6]:
            PillBottle.objects.create(
                container_type=container_type,
                name=f"BOTTLE_{i}",
                medication_lot=medication_lot_one,
                unit_qty=500,
                box=box_one,
            )

        source_pill_bottle = PillBottle.objects.get(name="BOTTLE_1")

        for i in [1, 2, 3]:
            _, source_pill_bottle = repackage(
                PillBottle, 128, box=box_two, source_container=source_pill_bottle
            )

        self.assertRaises(
            InsufficientQuantityError,
            repackage,
            PillBottle,
            128,
            box=box_two,
            source_container=source_pill_bottle,
        )

        self.assertEquals(
            source_pill_bottle.unit_qty - source_pill_bottle.unit_qty_out, 500 - (128 * 3)
        )

        for obj in PillBottle.objects.filter(source_container=source_pill_bottle):
            self.assertEquals(obj.unit_qty, 128)
