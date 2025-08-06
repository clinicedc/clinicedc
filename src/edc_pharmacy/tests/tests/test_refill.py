from dateutil.relativedelta import relativedelta
from django.test import TestCase
from edc_constants.constants import FEMALE
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow

from edc_pharmacy.exceptions import PrescriptionNotStarted
from edc_pharmacy.models import (
    DosageGuideline,
    Formulation,
    FormulationType,
    FrequencyUnits,
    Medication,
    Route,
    Rx,
    RxRefill,
    Units,
)
from edc_pharmacy.refill import (
    RefillCreator,
    activate_refill,
    deactivate_refill,
    get_active_refill,
)


class TestRefill(TestCase):
    def setUp(self):
        self.subject_identifier = "12345"

        report_datetime = get_utcnow() - relativedelta(days=60)
        RegisteredSubject.objects.create(
            subject_identifier="12345",
            dob=get_utcnow() - relativedelta(years=25),
            gender=FEMALE,
            registration_datetime=report_datetime,
            randomization_datetime=report_datetime,
        )

        self.medication = Medication.objects.create(
            name="Flucytosine",
            display_name="flucytosine",
        )

        # create prescription for this subject
        self.rx = Rx.objects.create(
            subject_identifier=self.subject_identifier,
            weight_in_kgs=40,
            report_datetime=report_datetime,
            rx_date=report_datetime.date(),
        )
        self.rx.medications.add(self.medication)

        self.formulation = Formulation.objects.create(
            medication=self.medication,
            strength=500,
            units=Units.objects.get(name="mg"),
            route=Route.objects.get(display_name="Oral"),
            formulation_type=FormulationType.objects.get(display_name__iexact="Tablet"),
        )

        self.dosage_guideline = DosageGuideline.objects.create(
            medication=self.medication,
            dose_per_kg=50,
            dose_units=Units.objects.get(name="mg"),
            frequency=1,
            frequency_units=FrequencyUnits.objects.get(name="day"),
        )

        self.dosage_guideline_no_weight = DosageGuideline.objects.create(
            medication=self.medication,
            dose=500,
            dose_units=Units.objects.get(name="mg"),
            frequency=2,
            frequency_units=FrequencyUnits.objects.get(name="day"),
        )

    def test_rx_refill_str(self):
        obj = RxRefill.objects.create(
            rx=self.rx,
            formulation=self.formulation,
            dosage_guideline=self.dosage_guideline,
            refill_start_datetime=get_utcnow(),
            refill_end_datetime=get_utcnow() + relativedelta(days=10),
            weight_in_kgs=65,
        )
        self.assertTrue(str(obj))

    def test_prescription_calculates_dose(self):
        """50mg /kg for 10 days = 65 * 50 * 10"""
        obj = RxRefill.objects.create(
            rx=self.rx,
            formulation=self.formulation,
            dosage_guideline=self.dosage_guideline,
            refill_start_datetime=get_utcnow(),
            refill_end_datetime=get_utcnow() + relativedelta(days=10),
            weight_in_kgs=65,
        )
        self.assertEqual(obj.dose, 6.5)
        self.assertEqual(obj.total, 65.0)  # 10 days
        self.assertEqual(obj.dosage_guideline.dose_units.name, "mg")
        self.assertEqual(obj.formulation.units.name, "mg")

    def test_prescription_total_to_dispense_or_order_without_roundup(self):
        obj = RxRefill.objects.create(
            rx=self.rx,
            formulation=self.formulation,
            dosage_guideline=self.dosage_guideline_no_weight,
            refill_start_datetime=get_utcnow(),
            refill_end_datetime=get_utcnow() + relativedelta(days=56),
        )
        self.assertEqual(obj.total, 112)

    def test_prescription_total_to_dispense_or_order_with_roundup(self):
        obj = RxRefill.objects.create(
            rx=self.rx,
            formulation=self.formulation,
            dosage_guideline=self.dosage_guideline_no_weight,
            refill_start_datetime=get_utcnow(),
            refill_end_datetime=get_utcnow() + relativedelta(days=56),
            roundup_divisible_by=32,
        )
        self.assertEqual(obj.total, 128)

    def test_prescription_total_to_dispense_or_order_weight_in_kgs(self):
        obj = RxRefill.objects.create(
            rx=self.rx,
            formulation=self.formulation,
            dosage_guideline=self.dosage_guideline,
            refill_start_datetime=get_utcnow(),
            refill_end_datetime=get_utcnow() + relativedelta(days=10),
            weight_in_kgs=65,
        )
        self.assertEqual(obj.dose, 6.5)  # 65kg * 50mg / 500mg = 6.5 pills
        self.assertEqual(obj.total, 65)  # x 10 days

    def test_prescription_total_to_dispense_or_order_weight_in_kgs_with_roundup(self):
        obj = RxRefill.objects.create(
            rx=self.rx,
            formulation=self.formulation,
            dosage_guideline=self.dosage_guideline,
            refill_start_datetime=get_utcnow(),
            refill_end_datetime=get_utcnow() + relativedelta(days=10),
            weight_in_kgs=65,
            roundup_divisible_by=12,
        )
        self.assertEqual(obj.dose, 6.5)  # 65kg * 50mg / 500mg = 6.5 pills
        self.assertEqual(obj.total, 72)

    def test_refill_gets_rx(self):
        refill_creator = RefillCreator(
            subject_identifier=self.subject_identifier,
            refill_start_datetime=get_utcnow(),
            refill_end_datetime=get_utcnow() + relativedelta(days=32),
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
            weight_in_kgs=65,
        )
        self.assertTrue(refill_creator.rx_refill.rx)

    def test_refill_raises_on_gets_rx(self):
        """Assert raises if refill date before Rx"""
        self.assertRaises(
            PrescriptionNotStarted,
            RefillCreator,
            subject_identifier=self.subject_identifier,
            refill_start_datetime=(get_utcnow() - relativedelta(years=1)),
            refill_end_datetime=get_utcnow() + relativedelta(days=32),
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
            weight_in_kgs=65,
        )

    def test_refill_create_and_no_active_refill(self):
        refill_creator = RefillCreator(
            subject_identifier=self.subject_identifier,
            refill_start_datetime=get_utcnow(),
            refill_end_datetime=get_utcnow() + relativedelta(days=32),
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
            make_active=False,
            weight_in_kgs=65,
        )
        self.assertIsNone(get_active_refill(refill_creator.rx_refill.rx))

    def test_refill_create_and_gets_active_refill(self):
        refill_creator = RefillCreator(
            subject_identifier=self.subject_identifier,
            refill_start_datetime=get_utcnow(),
            refill_end_datetime=get_utcnow() + relativedelta(days=32),
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
            weight_in_kgs=65,
        )
        self.assertEqual(
            get_active_refill(refill_creator.rx_refill.rx),
            refill_creator.rx_refill,
        )

    def test_refill_create_activates_by_default(self):
        refill_creator = RefillCreator(
            subject_identifier=self.subject_identifier,
            refill_start_datetime=get_utcnow(),
            refill_end_datetime=get_utcnow() + relativedelta(days=32),
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
            weight_in_kgs=65,
        )
        self.assertTrue(get_active_refill(refill_creator.rx_refill.rx).active)

    def test_refill_create_does_not_activate_if_false(self):
        refill_creator = RefillCreator(
            subject_identifier=self.subject_identifier,
            refill_start_datetime=get_utcnow(),
            refill_end_datetime=get_utcnow() + relativedelta(days=32),
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
            make_active=False,
            weight_in_kgs=65,
        )
        self.assertIsNone(get_active_refill(refill_creator.rx_refill.rx))

    def test_refill_create_duplicate_updates(self):
        # create a refill
        refill_start_datetime_one = get_utcnow() - relativedelta(days=60)
        RefillCreator(
            subject_identifier=self.subject_identifier,
            refill_start_datetime=refill_start_datetime_one,
            refill_end_datetime=refill_start_datetime_one + relativedelta(days=32),
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
            weight_in_kgs=65,
        )
        rx_refill_one = RxRefill.objects.get(
            rx__subject_identifier=self.subject_identifier,
            refill_start_datetime=refill_start_datetime_one,
        )
        self.assertEqual(rx_refill_one.number_of_days, 32)

        # create another refill but change number_of_days
        RefillCreator(
            subject_identifier=self.subject_identifier,
            refill_start_datetime=refill_start_datetime_one,
            refill_end_datetime=refill_start_datetime_one + relativedelta(days=31),
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
            weight_in_kgs=65,
        )
        rx_refill_two = RxRefill.objects.get(
            rx__subject_identifier=self.subject_identifier,
            refill_start_datetime=refill_start_datetime_one,
        )
        self.assertEqual(rx_refill_two.number_of_days, 31)
        self.assertEqual(rx_refill_two.id, rx_refill_one.id)

    def test_refill_create_finds_active(self):
        refill_creator = RefillCreator(
            subject_identifier=self.subject_identifier,
            refill_start_datetime=get_utcnow(),
            refill_end_datetime=get_utcnow() + relativedelta(days=32),
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
            make_active=True,
            weight_in_kgs=65,
        )
        self.assertIsNotNone(get_active_refill(refill_creator.rx_refill.rx))
        deactivate_refill(refill_creator.rx_refill)
        self.assertIsNone(get_active_refill(refill_creator.rx_refill.rx))

    def test_refill_create_activates_next(self):
        refill_creator = RefillCreator(
            subject_identifier=self.subject_identifier,
            refill_start_datetime=get_utcnow(),
            refill_end_datetime=get_utcnow() + relativedelta(days=32),
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
            weight_in_kgs=65,
        )
        self.assertIsNotNone(get_active_refill(refill_creator.rx_refill.rx))

        refill_creator = RefillCreator(
            subject_identifier=self.subject_identifier,
            refill_start_datetime=get_utcnow() + relativedelta(months=1),
            refill_end_datetime=get_utcnow() + relativedelta(days=32),
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
            make_active=True,
            weight_in_kgs=65,
        )
        self.assertIsNotNone(get_active_refill(refill_creator.rx_refill.rx))
        self.assertEqual(
            get_active_refill(refill_creator.rx_refill.rx), refill_creator.rx_refill
        )

    def test_refill_create_refill_start_datetime(self):
        refill_start_datetime = get_utcnow()
        refill_creator = RefillCreator(
            subject_identifier=self.subject_identifier,
            refill_start_datetime=refill_start_datetime,
            refill_end_datetime=get_utcnow() + relativedelta(days=32),
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
            weight_in_kgs=65,
        )

        self.assertEqual(refill_creator.rx_refill.refill_start_datetime, refill_start_datetime)

    def test_refill_create_and_make_active(self):
        refill_start_datetime = get_utcnow()
        refill_creator = RefillCreator(
            subject_identifier=self.subject_identifier,
            refill_start_datetime=refill_start_datetime,
            refill_end_datetime=get_utcnow() + relativedelta(days=32),
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
            make_active=False,
            weight_in_kgs=65,
        )
        self.assertFalse(refill_creator.rx_refill.active)
        activate_refill(refill_creator.rx_refill)
        self.assertTrue(refill_creator.rx_refill.active)
        self.assertEqual(RxRefill.objects.all().count(), 1)

    def test_refill_count(self):
        refill_start_datetime = get_utcnow()
        RefillCreator(
            subject_identifier=self.subject_identifier,
            refill_start_datetime=refill_start_datetime,
            refill_end_datetime=get_utcnow() + relativedelta(days=11),
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
            make_active=True,
            weight_in_kgs=65,
            roundup_divisible_by=0,
        )
        rx_refill = RxRefill.objects.get(rx__subject_identifier=self.subject_identifier)
        self.assertEqual(rx_refill.number_of_days, 11)
        self.assertEqual(rx_refill.dose, 6.5)  # (65 * 50)/500
        self.assertEqual(rx_refill.total, 71.5)  # 6.5 * 11
        self.assertEqual(rx_refill.remaining, 71.5)

    def test_refill_on_change(self):
        refill_start_datetime = get_utcnow()
        RefillCreator(
            subject_identifier=self.subject_identifier,
            refill_start_datetime=refill_start_datetime,
            refill_end_datetime=get_utcnow() + relativedelta(days=11),
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
            make_active=True,
            weight_in_kgs=65,
            roundup_divisible_by=0,
        )
        rx_refill = RxRefill.objects.get(rx__subject_identifier=self.subject_identifier)
        self.assertEqual(rx_refill.number_of_days, 11)
        refill_start_datetime = get_utcnow() + relativedelta(days=4)
        RefillCreator(
            subject_identifier=self.subject_identifier,
            refill_start_datetime=refill_start_datetime,
            refill_end_datetime=get_utcnow() + relativedelta(days=11),
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
            make_active=True,
            weight_in_kgs=65,
            roundup_divisible_by=0,
        )
        self.assertEqual(rx_refill.number_of_days, 11)
