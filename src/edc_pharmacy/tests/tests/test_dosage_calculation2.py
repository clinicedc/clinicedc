from django.test import TestCase
from edc_list_data import site_list_data

from edc_pharmacy.dosage_calculator import DosageCalculator
from edc_pharmacy.models import (
    DosageGuideline,
    Formulation,
    FormulationType,
    FrequencyUnits,
    Medication,
    Route,
    Units,
)


class TestDoseCalculator(TestCase):
    def setUp(self):
        site_list_data.initialize()
        site_list_data.autodiscover()
        self.medication = Medication.objects.create(
            name="Metformin",
            display_name="Metformin",
        )

        formulation_type = FormulationType.objects.get(name="tablet")

        self.formulation = Formulation.objects.create(
            medication=self.medication,
            strength=500,
            units=Units.objects.get(display_name__iexact="mg"),
            route=Route.objects.get(display_name__iexact="oral"),
            formulation_type=formulation_type,
        )
        self.dosage_guideline_baseline = DosageGuideline.objects.create(
            medication=self.medication,
            dose=1000.0,
            dose_units=Units.objects.get(display_name__iexact="mg"),
            frequency=1.0,
            frequency_units=FrequencyUnits.objects.get(display_name__iexact="times per day"),
        )
        self.dosage_guideline = DosageGuideline.objects.create(
            medication=self.medication,
            dose=2000.0,
            dose_units=Units.objects.get(display_name__iexact="mg"),
            frequency=1.0,
            frequency_units=FrequencyUnits.objects.get(display_name__iexact="times per day"),
        )

    def test_dosage_baseline(self):
        """2 tabs / day = 1000mg"""
        self.assertEqual(
            DosageCalculator(
                dosage_guideline=self.dosage_guideline_baseline, formulation=self.formulation
            ).dosage,
            2.0,
        )

    def test_dosage_post_baseline(self):
        """4 tabs / day = 2000mg"""
        self.assertEqual(
            DosageCalculator(
                dosage_guideline=self.dosage_guideline, formulation=self.formulation
            ).dosage,
            4.0,
        )
