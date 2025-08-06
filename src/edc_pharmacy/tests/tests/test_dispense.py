from dateutil.relativedelta import relativedelta
from django.test import TestCase
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow

from edc_pharmacy.models import (
    DosageGuideline,
    Formulation,
    FormulationType,
    FrequencyUnits,
    Medication,
    Route,
    Rx,
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
