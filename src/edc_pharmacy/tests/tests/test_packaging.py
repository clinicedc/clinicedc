from dateutil.relativedelta import relativedelta
from django.test import TestCase
from edc_facility import import_holidays
from edc_list_data import site_list_data
from edc_randomization.constants import ACTIVE, PLACEBO
from edc_randomization.site_randomizers import site_randomizers
from edc_randomization.tests.testcase_mixin import TestCaseMixin, all_sites
from edc_sites import add_or_update_django_sites
from edc_utils import get_utcnow

from edc_pharmacy.exceptions import InsufficientQuantityError
from edc_pharmacy.models import (
    Box,
    ContainerType,
    Formulation,
    FormulationType,
    Location,
    Medication,
    MedicationLot,
    PillBottle,
    Room,
    Route,
    Shelf,
    SubjectPillBottle,
    Units,
    repackage,
    repackage_for_subject,
)


class TestPackaging(TestCaseMixin, TestCase):
    import_randomization_list = True
    site_names = [x.name for x in all_sites]
    sid_count_for_tests = 5

    @classmethod
    def setUpTestData(cls):
        import_holidays(test=True)
        add_or_update_django_sites(sites=all_sites)
        if cls.import_randomization_list:
            randomizer_cls = site_randomizers.get("default")
            randomizer_cls.import_list(
                verbose=False, sid_count_for_tests=cls.sid_count_for_tests
            )
        site_list_data.initialize()
        site_list_data.autodiscover()

    def setUp(self):
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
        self.medication_lot_one = MedicationLot.objects.create(
            lot_no="LOT1111111",
            formulation=self.formulation,
            expiration_date=get_utcnow() + relativedelta(years=1),
            assignment=ACTIVE,
        )
        self.medication_lot_two = MedicationLot.objects.create(
            lot_no="LOT222222",
            formulation=self.formulation,
            expiration_date=get_utcnow() + relativedelta(years=1),
            assignment=PLACEBO,
        )

    def test_repack(self):
        container_type = ContainerType.objects.create(name="bottle")

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
                medication_lot=self.medication_lot_one,
                unit_qty=500,
                box=box_one,
            )

        source_pill_bottle = PillBottle.objects.get(name="BOTTLE_1")

        for _ in [1, 2, 3]:
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

    def test_repack_for_subject(self):
        container_type = ContainerType.objects.create(name="bottle")
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
                medication_lot=self.medication_lot_one,
                unit_qty=500,
                box=box_one,
            )

        source_pill_bottle = PillBottle.objects.get(name="BOTTLE_1")

        subject_pill_bottle, source_pill_bottle = repackage_for_subject(
            new_container_model_cls=SubjectPillBottle,
            unit_qty=32,
            randomizer_name="default",
            rando_sid="1001",
            subject_identifier=None,
            source_container=source_pill_bottle,
            box=box_two,
        )

        self.assertEqual(source_pill_bottle.unit_qty_out, 32)
        self.assertEqual(subject_pill_bottle.unit_qty, 32)
