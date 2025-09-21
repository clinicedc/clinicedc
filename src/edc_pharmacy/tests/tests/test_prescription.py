from tempfile import mkdtemp

from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.sites import all_sites
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, override_settings, tag
from django.utils import timezone

from edc_consent import site_consents
from edc_facility.import_holidays import import_holidays
from edc_list_data import site_list_data
from edc_pharmacy.exceptions import PrescriptionAlreadyExists, PrescriptionError
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
from edc_pharmacy.prescribe import create_prescription
from edc_randomization.randomizer import Randomizer
from edc_randomization.site_randomizers import site_randomizers
from edc_randomization.tests.utils import populate_randomization_list_for_tests
from edc_sites.site import sites
from edc_sites.utils import add_or_update_django_sites
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


class MyRandomizer(Randomizer):
    name = "my_randomizer"
    model = "clinicedc_tests.CustomRandomizationList"
    randomizationlist_folder = mkdtemp()


@tag("pharmacy")
@override_settings(EDC_RANDOMIZATION_REGISTER_DEFAULT_RANDOMIZER=False, SITE_ID=10)
class TestPrescription(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        sites._registry = {}
        sites.loaded = False
        sites.register(*all_sites)
        add_or_update_django_sites()

        site_randomizers.register(MyRandomizer)
        populate_randomization_list_for_tests(
            MyRandomizer.name, site_names=["mochudi"], per_site=15
        )

    def setUp(self):
        site_list_data.initialize()
        site_list_data.autodiscover()
        site_consents.registry = {}
        site_consents.register(consent_v1)

        visit_schedule = get_visit_schedule(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)

        helper = Helper()
        self.subject_consent = helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule", schedule_name="schedule"
        )

        site_randomizers.randomize(
            "my_randomizer",
            subject_identifier=self.subject_consent.subject_identifier,
            report_datetime=self.subject_consent.consent_datetime,
            site=self.subject_consent.site,
            user=self.subject_consent.user_created or "jasper_the_dog",
            gender=self.subject_consent.gender,
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
            subject_identifier=self.subject_consent.subject_identifier,
            report_datetime=timezone.now(),
        )
        obj.medications.add(self.medication)
        obj.save()

    def test_verify_prescription(self):
        obj = Rx.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            report_datetime=timezone.now(),
        )
        obj.medications.add(self.medication)
        obj.verified = True
        obj.verified = timezone.now()
        obj.save()
        self.assertTrue(obj.verified)

    def test_create_prescripition_from_func(self):
        create_prescription(
            subject_identifier=self.subject_consent.subject_identifier,
            report_datetime=self.subject_consent.consent_datetime,
            randomizer_name="my_randomizer",
            medication_names=[self.medication.name],
            site=self.subject_consent.site,
        )
        try:
            Rx.objects.get(subject_identifier=self.subject_consent.subject_identifier)
        except ObjectDoesNotExist:
            self.fail("Rx unexpectedly does not exist")

    def test_create_prescripition_already_exists(self):
        create_prescription(
            subject_identifier=self.subject_consent.subject_identifier,
            report_datetime=self.subject_consent.consent_datetime,
            randomizer_name="my_randomizer",
            medication_names=[self.medication.name],
            site=self.subject_consent.site,
        )
        Rx.objects.get(subject_identifier=self.subject_consent.subject_identifier)
        with self.assertRaises(PrescriptionAlreadyExists):
            create_prescription(
                subject_identifier=self.subject_consent.subject_identifier,
                report_datetime=self.subject_consent.consent_datetime,
                medication_names=[self.medication.name],
                randomizer_name="my_randomizer",
                site=self.subject_consent.site,
            )

    def test_create_prescripition_from_func_bad_medication(self):
        try:
            create_prescription(
                subject_identifier=self.subject_consent.subject_identifier,
                report_datetime=self.subject_consent.consent_datetime,
                medication_names=[self.medication.name, "blah blah"],
                randomizer_name="my_randomizer",
                site=self.subject_consent.site,
            )
        except PrescriptionError:
            pass
        else:
            self.fail("PrescriptionError not raised")
