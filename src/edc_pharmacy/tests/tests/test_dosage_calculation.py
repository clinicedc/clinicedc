from django.test import TestCase, tag
from edc_list_data import site_list_data
from edc_pharmacy.dosage_per_day import DosageError, dosage_per_day
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

    @tag("14")
    def test_dosage_flucytosine(self):
        medication = Medication.objects.get(name="flucytosine")
        dosage_guideline = DosageGuideline.objects.create(
            medication=medication,
            dose_per_kg=100.0,
            dose_units=Units.objects.get(display_name__iexact="mg"),
            frequency=1.0,
            frequency_units=FrequencyUnits.objects.get(
                display_name__iexact="times per day"
            ),
        )
        self.assertEqual(
            dosage_per_day(dosage_guideline, strength=100.0, strength_units="mg"), 1.0
        )
        self.assertEqual(
            dosage_per_day(
                dosage_guideline,
                weight_in_kgs=40.0,
                strength=500.0,
                strength_units="mg",
            ),
            8.0,
        )

    def test_dosage_ambisome(self):
        medication = Medication.objects.get(name="ambisome")
        dosage_guideline = DosageGuideline.objects.create(
            medication=medication,
            dose_per_kg=10.0,
            dose_units=Units.objects.get(display_name__iexact="mg"),
            frequency=1.0,
            frequency_units=FrequencyUnits.objects.get(
                display_name__iexact="times per day"
            ),
        )
        self.assertEqual(
            dosage_per_day(dosage_guideline, strength=1.0, strength_units="mg"),
            10.0,
        )
        self.assertEqual(
            dosage_per_day(
                dosage_guideline, weight_in_kgs=40.0, strength=50.0, strength_units="mg"
            ),
            8.0,
        )

    def test_dosage_flucanazole(self):
        medication = Medication.objects.get(name="flucanazole")
        dosage_guideline = DosageGuideline.objects.create(
            medication=medication,
            dose=1200.0,
            dose_units=Units.objects.get(display_name__iexact="mg"),
            frequency=1.0,
            frequency_units=FrequencyUnits.objects.get(
                display_name__iexact="times per day"
            ),
        )
        self.assertEqual(
            dosage_per_day(dosage_guideline, strength=1.0, strength_units="mg"), 1200.0
        )
        self.assertEqual(
            dosage_per_day(dosage_guideline, strength=200, strength_units="mg"), 6.0
        )

    def test_dosage_exceptions(self):
        medication = Medication.objects.get(name="flucytosine")
        dosage_guideline = DosageGuideline.objects.create(
            medication=medication,
            dose_per_kg=100,
            dose_units=Units.objects.get(display_name__iexact="mg"),
            frequency=1,
            frequency_units=FrequencyUnits.objects.get(
                display_name__iexact="times per day"
            ),
        )

        self.assertRaises(
            DosageError,
            dosage_per_day,
            dosage_guideline,
            weight_in_kgs=40,
            strength=500,
            strength_units="kg",
        )
