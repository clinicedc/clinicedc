from django.test import TestCase, tag

from ..choices import DRUG_FORMULATION
from ..dosage_calculator import DosageGuidelineError
from ..models import Medication, DosageGuideline


class TestDoseCalculator(TestCase):

    def setUp(self):

        Medication.objects.create(
            name='Flucytosine',
            strength=500,
            units='mg',
            route='30',  # oral
            formulation=DRUG_FORMULATION[0][0])

        Medication.objects.create(
            name='Flucanazole',
            strength=200,
            units='mg',
            route='30',  # oral
            formulation=DRUG_FORMULATION[0][0])

        Medication.objects.create(
            name='Ambisome',
            strength=50,
            units='mg',
            route='20',  # intravenous
            formulation=DRUG_FORMULATION[0][0])

    def test_dosage_flucytosine(self):
        dosage_guideline = DosageGuideline.objects.create(
            medication_name='Flucytosine',
            dose_per_kg=100,
            dose_units='mg',
            dose_frequency_factor=1,
            dose_frequency_units='per_day',
            subject_weight_factor=1)
        self.assertEqual(dosage_guideline.dosage_per_kg_per_day, 100.0)
        self.assertEqual(dosage_guideline.dosage_per_day(
            weight_in_kgs=40, strength=500, strength_units='mg'), 8.0)

    def test_dosage_ambisome(self):
        dosage_guideline = DosageGuideline.objects.create(
            medication_name='Ambisome',
            dose_per_kg=10,
            dose_units='mg',
            dose_frequency_factor=1,
            dose_frequency_units='per_day',
            subject_weight_factor=1)
        self.assertEqual(dosage_guideline.dosage_per_kg_per_day, 10.0)
        self.assertEqual(dosage_guideline.dosage_per_day(
            weight_in_kgs=40, strength=50, strength_units='mg'), 8.0)

    def test_dosage_flucanazole(self):
        dosage_guideline = DosageGuideline.objects.create(
            medication_name='Flucanazole',
            dose=1200,
            dose_units='mg',
            dose_frequency_factor=1,
            dose_frequency_units='per_day',
            subject_weight_factor=1)
        self.assertIsNone(dosage_guideline.dosage_per_kg_per_day)
        self.assertEqual(dosage_guideline.dosage_per_day(
            strength=200, strength_units='mg'), 6.0)

    def test_dosage_exceptions(self):
        dosage_guideline = DosageGuideline.objects.create(
            medication_name='Flucytosine',
            dose_per_kg=100,
            dose_units='mg',
            dose_frequency_factor=1,
            dose_frequency_units='per_day',
            subject_weight_factor=1)

        self.assertRaises(
            DosageGuidelineError,
            dosage_guideline.dosage_per_day,
            weight_in_kgs=40, strength=100, strength_units='mg')

        self.assertRaises(
            DosageGuidelineError,
            dosage_guideline.dosage_per_day,
            weight_in_kgs=40, strength=500, strength_units='kg')
