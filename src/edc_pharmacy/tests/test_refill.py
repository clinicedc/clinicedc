from dateutil.relativedelta import relativedelta
from django.test import TestCase
from edc_pharmacy.dispensing import DispenseError
from edc_pharmacy.models import FormulationType, Route, Units
from edc_utils import get_utcnow

from ..models import (
    DispensingHistory,
    DosageGuideline,
    Formulation,
    Medication,
    Rx,
    RxRefill,
)


class TestRefill(TestCase):
    def setUp(self):
        self.subject_identifier = "12345"
        self.medication = Medication.objects.create(
            name="Flucytosine",
        )

        self.formulation = Formulation.objects.create(
            strength=500,
            units=Units.objects.get(name="mg"),
            route=Route.objects.get(display_name="Oral"),
            formulation=FormulationType.objects.get(display_name__iexact="Tablet"),
        )

        self.dosage_guideline = DosageGuideline.objects.create(
            medication=self.medication,
            dose_per_kg=100,
            dose_units="mg",
            frequency=1,
            frequency_units="per_day",
            subject_weight_factor=1,
        )
        self.rx = Rx.objects.create(
            subject_identifier=self.subject_identifier,
            weight_in_kgs=40,
            report_datetime=get_utcnow(),
            medication=self.medication,
        )

    def test_rx_refill_duration(self):
        obj = RxRefill.objects.create(
            rx=self.rx,
            medication=self.medication,
            dosage_guideline=self.dosage_guideline,
            frequency=1,
            start_date=get_utcnow(),
            end_date=get_utcnow() + relativedelta(days=10),
        )
        self.assertEqual(obj.rduration.days, 10)

    def test_prescription_str(self):
        obj = RxRefill.objects.create(
            rx=self.rx,
            medication=self.medication,
            dosage_guideline=self.dosage_guideline,
            frequency=1,
            start_date=get_utcnow(),
            end_date=get_utcnow() + relativedelta(days=10),
        )
        self.assertTrue(str(obj))

    def test_prescription_accepts_explicit_dose(self):
        obj = RxRefill.objects.create(
            rx=self.rx,
            medication=self.medication,
            dosage_guideline=self.dosage_guideline,
            frequency=1,
            dose=3,
            start_date=get_utcnow(),
            end_date=get_utcnow() + relativedelta(days=10),
        )
        self.assertEqual(obj.dose, 3)

    def test_prescription_calculates_dose(self):
        obj = RxRefill.objects.create(
            rx=self.rx,
            medication=self.medication,
            dosage_guideline=self.dosage_guideline,
            frequency=1,
            dose=None,
            start_date=get_utcnow(),
            end_date=get_utcnow() + relativedelta(days=10),
        )
        self.assertEqual(obj.dose, 8.0)
        self.assertEqual(obj.medication.units, "mg")

    def test_prescription_total(self):
        obj = RxRefill.objects.create(
            rx=self.rx,
            medication=self.medication,
            dosage_guideline=self.dosage_guideline,
            frequency=1,
            dose=None,
            start_date=get_utcnow(),
            end_date=get_utcnow() + relativedelta(days=7),
        )
        self.assertEqual(obj.total, 56)

    def test_dispense(self):
        rx_refill = RxRefill.objects.create(
            rx=self.rx,
            medication=self.medication,
            dosage_guideline=self.dosage_guideline,
            frequency=1,
            dose=None,
            start_date=get_utcnow(),
            end_date=get_utcnow() + relativedelta(days=7),
        )
        obj = DispensingHistory.objects.create(
            rx=self.rx,
            rx_refill=rx_refill,
            dispensed=8,
        )
        self.assertEqual(obj.dispensed, 8)
        rx_refill = RxRefill.objects.get(id=rx_refill.id)
        self.assertEqual(rx_refill.remaining, 56 - 8)

    def test_dispense_many(self):
        rx_refill = RxRefill.objects.create(
            rx=self.rx,
            medication=self.medication,
            dosage_guideline=self.dosage_guideline,
            frequency=1,
            dose=None,
            start_date=get_utcnow(),
            end_date=get_utcnow() + relativedelta(days=7),
        )
        dispensed = 0
        for amount in [8, 8, 8]:
            dispensed += amount
            obj = DispensingHistory.objects.create(
                rx=self.rx,
                rx_refill=rx_refill,
                dispensed=8,
            )
            self.assertEqual(obj.dispensed, 8)
            rx_refill = RxRefill.objects.get(id=rx_refill.id)
            self.assertEqual(rx_refill.remaining, 56 - dispensed)

    def test_attempt_to_over_dispense(self):
        rx_refill = RxRefill.objects.create(
            rx=self.rx,
            medication=self.medication,
            dosage_guideline=self.dosage_guideline,
            frequency=1,
            dose=None,
            start_date=get_utcnow(),
            end_date=get_utcnow() + relativedelta(days=7),
        )
        dispensed = 0
        for amount in [8, 8, 8, 8, 8, 8, 8]:
            dispensed += amount
            obj = DispensingHistory.objects.create(
                rx=self.rx,
                rx_refill=rx_refill,
                dispensed=8,
            )
            self.assertEqual(obj.dispensed, 8)
            rx_refill = RxRefill.objects.get(id=rx_refill.id)
            self.assertEqual(rx_refill.remaining, 56 - dispensed)
        rx_refill = RxRefill.objects.get(id=rx_refill.id)
        self.assertEqual(rx_refill.remaining, 0)
        self.assertRaises(
            DispenseError,
            DispensingHistory.objects.create,
            rx=self.rx,
            rx_refill=rx_refill,
            dispensed=8,
        )
