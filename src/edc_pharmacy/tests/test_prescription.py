from dateutil.relativedelta import relativedelta
from django.test import TestCase
from edc_constants.constants import FEMALE
from edc_list_data import site_list_data
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow

from ..models import FormulationType, Medication, Route, Rx, Units


class TestPrescription(TestCase):
    def setUp(self):
        site_list_data.initialize()
        site_list_data.autodiscover()
        self.registered_subject = RegisteredSubject.objects.create(
            subject_identifier="12345",
            gender=FEMALE,
            dob=get_utcnow() - relativedelta(years=25),
        )
        self.medication = Medication.objects.create(
            name="Augmentin",
            strength=200,
            units=Units.objects.get(name="mg"),
            route=Route.objects.get(display_name__iexact="intravenous"),
            formulation_type=FormulationType.objects.all()[0],
        )

    def test_medication_description(self):
        self.assertEqual(str(self.medication), "Augmentin 200mg. Tablet Oral")

    def test_create_prescription(self):
        obj = Rx.objects.create(
            registered_subject=self.registered_subject,
            report_datetime=get_utcnow(),
            medication=self.medication,
        )
        obj.save()

    def test_verify_prescription(self):
        obj = Rx.objects.create(
            registered_subject=self.registered_subject,
            report_datetime=get_utcnow(),
            medication=self.medication,
        )
        obj.verified = True
        obj.verified = get_utcnow()
        obj.save()
        self.assertTrue(obj.verified)
