from django.test import TestCase
from edc_list_data import site_list_data

from edc_pharmacy.dosage_calculator import DosageCalculator
from edc_pharmacy.dosage_per_day import DosageError
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
        medication = Medication.objects.create(
            name="flucytosine",
            display_name="Flucytosine",
        )

        Formulation.objects.create(
            medication=medication,
            strength=500,
            units=Units.objects.get(display_name__iexact="mg"),
            route=Route.objects.get(display_name__iexact="oral"),
            formulation_type=FormulationType.objects.all()[0],
        )

        medication = Medication.objects.create(
            name="flucanazole",
            display_name="Flucanazole",
        )

        Formulation.objects.create(
            medication=medication,
            strength=200,
            units=Units.objects.get(display_name__iexact="mg"),
            route=Route.objects.get(display_name__iexact="oral"),
            formulation_type=FormulationType.objects.all()[0],
        )

        medication = Medication.objects.create(
            name="ambisome",
            display_name="Ambisome",
        )

        Formulation.objects.create(
            medication=medication,
            strength=50,
            units=Units.objects.get(display_name__iexact="mg"),
            route=Route.objects.get(display_name__iexact="intravenous"),
            formulation_type=FormulationType.objects.all()[0],
        )

    def test_dosage_flucytosine(self):
        medication = Medication.objects.get(name="flucytosine")
        dosage_guideline = DosageGuideline.objects.create(
            medication=medication,
            dose_per_kg=100.0,
            dose_units=Units.objects.get(display_name__iexact="mg"),
            frequency=1.0,
            frequency_units=FrequencyUnits.objects.get(display_name__iexact="times per day"),
        )
        formulation = Formulation.objects.get(
            medication=medication,
        )

        self.assertEqual(
            DosageCalculator(
                dosage_guideline=dosage_guideline,
                formulation=formulation,
                weight_in_kgs=100.0,
            ).dosage,
            20.0,
        )
        self.assertEqual(
            DosageCalculator(
                dosage_guideline=dosage_guideline,
                formulation=formulation,
                weight_in_kgs=40.0,
            ).dosage,
            8.0,
        )

    def test_dosage_ambisome(self):
        medication = Medication.objects.get(name="ambisome")
        dosage_guideline = DosageGuideline.objects.create(
            medication=medication,
            dose_per_kg=10.0,
            dose_units=Units.objects.get(display_name__iexact="mg"),
            frequency=1.0,
            frequency_units=FrequencyUnits.objects.get(display_name__iexact="times per day"),
        )
        formulation = Formulation.objects.get(medication=medication)
        self.assertEqual(
            DosageCalculator(
                dosage_guideline=dosage_guideline, formulation=formulation, weight_in_kgs=40.0
            ).dosage,
            8.0,
        )

    def test_dosage_flucanazole(self):
        medication = Medication.objects.get(name="flucanazole")
        dosage_guideline = DosageGuideline.objects.create(
            medication=medication,
            dose=1200.0,
            dose_units=Units.objects.get(display_name__iexact="mg"),
            frequency=1.0,
            frequency_units=FrequencyUnits.objects.get(display_name__iexact="times per day"),
        )
        formulation = Formulation.objects.get(medication=medication)
        self.assertEqual(
            DosageCalculator(
                dosage_guideline=dosage_guideline, formulation=formulation
            ).dosage,
            6.0,
        )

    def test_dosage_exceptions(self):
        medication = Medication.objects.get(name="flucytosine")
        dosage_guideline = DosageGuideline.objects.create(
            medication=medication,
            dose_per_kg=100,
            dose_units=Units.objects.get(display_name__iexact="mg"),
            frequency=1,
            frequency_units=FrequencyUnits.objects.get(display_name__iexact="times per day"),
        )

        formulation = Formulation.objects.create(
            medication=medication,
            strength=200,
            units=Units.objects.get(display_name__iexact="g"),
            route=Route.objects.get(display_name__iexact="oral"),
            formulation_type=FormulationType.objects.all()[0],
        )

        self.assertRaises(
            DosageError,
            DosageCalculator,
            dosage_guideline=dosage_guideline,
            formulation=formulation,
            weight_in_kgs=40,
        )
