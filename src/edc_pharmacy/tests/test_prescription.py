from django.test import TestCase
from edc_utils import get_utcnow

from ..choices import DRUG_FORMULATION, DRUG_ROUTE
from ..models import Medication, Prescription


class TestPrescription(TestCase):
    def setUp(self):
        self.subject_identifier = "12345"
        self.medication = Medication.objects.create(
            name="Augmentin",
            strength=200,
            units="mg",
            route=DRUG_ROUTE[2][0],
            formulation=DRUG_FORMULATION[0][0],
        )

    def test_medication_description(self):
        self.assertEqual(str(self.medication), "Augmentin 200mg. Tablet Oral")

    def test_create_prescription(self):
        obj = Prescription.objects.create(
            subject_identifier=self.subject_identifier, report_datetime=get_utcnow()
        )
        obj.save()

    def test_verify_prescription(self):
        obj = Prescription.objects.create(
            subject_identifier=self.subject_identifier, report_datetime=get_utcnow()
        )
        obj.verified = True
        obj.verified = get_utcnow()
        obj.save()
        self.assertTrue(obj.verified)
