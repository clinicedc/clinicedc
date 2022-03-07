from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag
from edc_constants.constants import FEMALE
from edc_pharmacy.exceptions import (
    ActivePrescriptionRefillExists,
    PrescriptionError,
    PrescriptionRefillError,
)
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
from edc_pharmacy.refill import RefillCreator
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow


class TestRefill(TestCase):
    def setUp(self):
        self.subject_identifier = "12345"

        RegisteredSubject.objects.create(
            subject_identifier="12345",
            dob=get_utcnow() - relativedelta(years=25),
            gender=FEMALE,
        )

        self.medication = Medication.objects.create(
            name="Flucytosine",
            display_name="flucytosine",
        )

        self.formulation = Formulation.objects.create(
            medication=self.medication,
            strength=500,
            units=Units.objects.get(name="mg"),
            route=Route.objects.get(display_name="Oral"),
            formulation_type=FormulationType.objects.get(display_name__iexact="Tablet"),
        )

        self.dosage_guideline = DosageGuideline.objects.create(
            medication=self.medication,
            dose_per_kg=100,
            dose_units=Units.objects.get(name="mg"),
            frequency=1,
            frequency_units=FrequencyUnits.objects.get(name="day"),
        )

        self.rx = Rx.objects.create(
            subject_identifier=self.subject_identifier,
            weight_in_kgs=40,
            report_datetime=get_utcnow(),
            medication=self.medication,
        )

    def test_rx_refill_str(self):
        obj = RxRefill.objects.create(
            rx=self.rx,
            formulation=self.formulation,
            dosage_guideline=self.dosage_guideline,
            frequency=1,
            refill_date=get_utcnow(),
            number_of_days=10,
        )
        self.assertTrue(str(obj))

    def test_prescription_accepts_explicit_dose(self):
        obj = RxRefill.objects.create(
            rx=self.rx,
            formulation=self.formulation,
            dosage_guideline=self.dosage_guideline,
            frequency=1,
            dose=3,
            refill_date=get_utcnow(),
            number_of_days=10,
        )
        self.assertEqual(obj.dose, 3)

    def test_prescription_calculates_dose(self):
        obj = RxRefill.objects.create(
            rx=self.rx,
            formulation=self.formulation,
            dosage_guideline=self.dosage_guideline,
            frequency=1,
            dose=None,
            refill_date=get_utcnow(),
            number_of_days=10,
        )
        self.assertEqual(obj.dose, 8.0)
        self.assertEqual(obj.medication.units, "mg")

    def test_prescription_total(self):
        obj = RxRefill.objects.create(
            rx=self.rx,
            formulation=self.formulation,
            dosage_guideline=self.dosage_guideline,
            frequency=1,
            dose=None,
            refill_date=get_utcnow(),
            number_of_days=10,
        )
        self.assertEqual(obj.total, 56)

    @tag("35")
    def test_refill_gets_rx(self):
        refill_creator = RefillCreator(
            self.subject_identifier,
            refill_date=get_utcnow(),
            number_of_days=32,
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
        )
        self.assertTrue(refill_creator.rx)

    @tag("35")
    def test_refill_raises_on_gets_rx(self):
        """Assert raises if refill date before Rx"""
        self.assertRaises(
            PrescriptionError,
            RefillCreator,
            self.subject_identifier,
            refill_date=get_utcnow() - relativedelta(years=1),
            number_of_days=32,
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
        )

    @tag("35")
    def test_refill_create_and_no_active_refill(self):
        refill_creator = RefillCreator(
            self.subject_identifier,
            refill_date=get_utcnow(),
            number_of_days=32,
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
            make_active=False,
        )
        self.assertIsNone(refill_creator.active_refill)

    @tag("35")
    def test_refill_create_and_gets_active_refill(self):
        refill_creator = RefillCreator(
            self.subject_identifier,
            refill_date=get_utcnow(),
            number_of_days=32,
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
        )
        self.assertTrue(refill_creator.active_refill)
        self.assertTrue(refill_creator.active_refill.active)
        self.assertEqual(refill_creator.object, refill_creator.active_refill)

    @tag("35")
    def test_refill_create_activates_by_default(self):
        refill = RefillCreator(
            self.subject_identifier,
            refill_date=get_utcnow().date(),
            number_of_days=32,
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
        )
        self.assertTrue(refill.object.active)

    @tag("35")
    def test_refill_create_does_not_activate_if_false(self):
        refill = RefillCreator(
            self.subject_identifier,
            refill_date=get_utcnow().date(),
            number_of_days=32,
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
            make_active=False,
        )
        self.assertFalse(refill.object.active)

    @tag("35")
    def test_refill_create_duplicate_raises(self):
        RefillCreator(
            self.subject_identifier,
            refill_date=get_utcnow(),
            number_of_days=32,
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
        )
        self.assertRaises(
            PrescriptionRefillError,
            RefillCreator,
            self.subject_identifier,
            refill_date=get_utcnow(),
            number_of_days=32,
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
        )

    @tag("35")
    def test_refill_create_finds_active(self):
        refill_creator = RefillCreator(
            self.subject_identifier,
            refill_date=get_utcnow(),
            number_of_days=32,
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
            make_active=True,
        )
        self.assertIsNotNone(refill_creator.active_refill)
        refill_creator.object.active = False
        refill_creator.object.save()
        refill_creator.object.refresh_from_db()
        self.assertIsNone(refill_creator.active_refill)

    @tag("35")
    def test_refill_create_activates_next(self):
        refill_creator1 = RefillCreator(
            self.subject_identifier,
            refill_date=get_utcnow(),
            number_of_days=32,
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
        )
        refill_creator2 = RefillCreator(
            self.subject_identifier,
            refill_date=get_utcnow() + relativedelta(months=1),
            number_of_days=32,
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
            make_active=True,
        )
        refill_creator1.object.refresh_from_db()
        self.assertFalse(refill_creator1.object.active)
        self.assertTrue(refill_creator2.object.active)
        refill_creator1.object.active = True
        self.assertRaises(ActivePrescriptionRefillExists, refill_creator1.object.save)

    @tag("35")
    def test_refill_create_refill_date(self):
        refill_date = get_utcnow().date()
        refill_creator = RefillCreator(
            self.subject_identifier,
            refill_date=refill_date,
            number_of_days=32,
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
        )

        self.assertEqual(refill_creator.object.refill_date, refill_date)
