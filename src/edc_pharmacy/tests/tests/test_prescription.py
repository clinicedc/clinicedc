from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag
from edc_constants.constants import FEMALE
from edc_list_data import site_list_data
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
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow


@tag("35")
class TestPrescription(TestCase):
    def setUp(self):
        site_list_data.initialize()
        site_list_data.autodiscover()
        self.subject_identifier = "12345"
        self.registered_subject = RegisteredSubject.objects.create(
            subject_identifier=self.subject_identifier,
            gender=FEMALE,
            dob=get_utcnow() - relativedelta(years=25),
        )
        self.medication = Medication.objects.create(
            name="Flucytosine",
        )

        self.formulation = Formulation.objects.create(
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

    def test_create_prescription(self):
        obj = Rx.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow(),
            medication=self.medication,
        )
        obj.save()

    def test_verify_prescription(self):
        obj = Rx.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow(),
            medication=self.medication,
        )
        obj.verified = True
        obj.verified = get_utcnow()
        obj.save()
        self.assertTrue(obj.verified)
