from dateutil.relativedelta import relativedelta
from django.test import TestCase
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow

from edc_pharmacy.dispense import DispenseError
from edc_pharmacy.models import (
    DispensingHistory,
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


class TestDispense(TestCase):
    def setUp(self):
        self.subject_identifier = "12345"

        RegisteredSubject.objects.create(subject_identifier="12345")

        self.medication = Medication.objects.create(
            name="flucytosine",
            display_name="Flucytosine",
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
        )
        self.rx.medications.add(self.medication)

    def test_dispense(self):
        refill_creator = RefillCreator(
            subject_identifier=self.subject_identifier,
            refill_start_datetime=get_utcnow(),
            refill_end_datetime=get_utcnow() + relativedelta(days=7),
            dosage_guideline=self.dosage_guideline,
            formulation=self.formulation,
        )
        self.assertEqual(refill_creator.rx_refill.total, 56.0)
        self.assertEqual(refill_creator.rx_refill.remaining, 56.0)

    def test_dispense_many(self):
        rx_refill = RxRefill.objects.create(
            rx=self.rx,
            formulation=self.formulation,
            dosage_guideline=self.dosage_guideline,
            refill_start_datetime=get_utcnow(),
            refill_end_datetime=get_utcnow() + relativedelta(days=7),
            weight_in_kgs=50,
        )
        dispensed = 0
        self.assertEqual(rx_refill.total, 70.0)
        for amount in [8, 8, 8]:
            dispensed += amount
            obj = DispensingHistory.objects.create(
                rx_refill=rx_refill,
                dispensed=8,
            )
            self.assertEqual(obj.dispensed, 8)
            rx_refill = RxRefill.objects.get(id=rx_refill.id)
            self.assertEqual(rx_refill.remaining, 70 - dispensed)

    def test_attempt_to_over_dispense(self):
        rx_refill = RxRefill.objects.create(
            rx=self.rx,
            formulation=self.formulation,
            dosage_guideline=self.dosage_guideline,
            refill_start_datetime=get_utcnow(),
            refill_end_datetime=get_utcnow() + relativedelta(days=8),
            weight_in_kgs=45,
        )
        dispensed = 0
        self.assertEqual(rx_refill.total, 72.0)
        for amount in [8, 8, 8, 8, 8, 8, 8, 8]:
            dispensed += amount
            obj = DispensingHistory.objects.create(
                rx_refill=rx_refill,
                dispensed=8,
            )
            self.assertEqual(obj.dispensed, 8)
            rx_refill = RxRefill.objects.get(id=rx_refill.id)
            self.assertEqual(rx_refill.remaining, 72 - dispensed)
        rx_refill = RxRefill.objects.get(id=rx_refill.id)
        self.assertEqual(rx_refill.remaining, 8)
        self.assertRaises(
            DispenseError,
            DispensingHistory.objects.create,
            rx_refill=rx_refill,
            dispensed=16,
        )
