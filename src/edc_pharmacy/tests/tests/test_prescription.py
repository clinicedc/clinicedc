from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from edc_constants.constants import FEMALE
from edc_list_data import site_list_data
from edc_randomization.site_randomizers import site_randomizers
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow

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


class TestPrescription(TestCase):
    def setUp(self):
        site_list_data.initialize()
        site_list_data.autodiscover()
        self.subject_identifier = "12345"
        self.registered_subject = RegisteredSubject.objects.create(
            subject_identifier=self.subject_identifier,
            gender=FEMALE,
            dob=get_utcnow() - relativedelta(years=25),
            registration_datetime=get_utcnow(),
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
        )
        obj.medications.add(self.medication)
        obj.save()

    def test_verify_prescription(self):
        obj = Rx.objects.create(
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow(),
        )
        obj.medications.add(self.medication)
        obj.verified = True
        obj.verified = get_utcnow()
        obj.save()
        self.assertTrue(obj.verified)

    def test_create_prescripition_from_func(self):
        create_prescription(
            subject_identifier=self.registered_subject.subject_identifier,
            report_datetime=self.registered_subject.registration_datetime,
            medications=[self.medication],
            site=self.registered_subject.site,
        )
        try:
            Rx.objects.get(subject_identifier=self.registered_subject.subject_identifier)
        except ObjectDoesNotExist:
            self.fail("Rx unexpectedly does not exist")

    def test_create_prescripition_already_exists(self):
        create_prescription(
            subject_identifier=self.registered_subject.subject_identifier,
            report_datetime=self.registered_subject.registration_datetime,
            medications=[self.medication],
            site=self.registered_subject.site,
        )
        Rx.objects.get(subject_identifier=self.registered_subject.subject_identifier)
        with self.assertRaises(PrescriptionAlreadyExists):
            create_prescription(
                subject_identifier=self.registered_subject.subject_identifier,
                report_datetime=self.registered_subject.registration_datetime,
                medications=[self.medication],
                site=self.registered_subject.site,
            )

    def test_create_prescripition_from_func_for_rct(self):
        randomizer = site_randomizers.get("default")
        randomizer.import_list(verbose=False, sid_count_for_tests=3)
        site_randomizers.randomize(
            "default",
            subject_identifier=self.registered_subject.subject_identifier,
            report_datetime=get_utcnow(),
            site=self.registered_subject.site,
            user="jasper",
            gender=self.registered_subject.gender,
        )
        create_prescription(
            subject_identifier=self.registered_subject.subject_identifier,
            report_datetime=self.registered_subject.registration_datetime,
            randomizer_name="default",
            medications=[self.medication],
            site=self.registered_subject.site,
        )
        try:
            Rx.objects.get(subject_identifier=self.registered_subject.subject_identifier)
        except ObjectDoesNotExist:
            self.fail("Rx unexpectedly does not exist")

    def test_create_prescripition_from_func_bad_medication(self):
        try:
            create_prescription(
                subject_identifier=self.registered_subject.subject_identifier,
                report_datetime=self.registered_subject.registration_datetime,
                medications=[self.medication, "blah blah"],
                site=self.registered_subject.site,
            )
        except PrescriptionError:
            pass
        else:
            self.fail("PrescriptionError not raised")
