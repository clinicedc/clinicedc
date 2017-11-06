from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag
from edc_base.utils import get_utcnow

from ..models import DosageGuideline, DispensedItem, DispenseError
from ..models import Prescription, Medication, PrescriptionItem


class TestPrescription(TestCase):

    def setUp(self):
        self.subject_identifier = '12345'
        self.medication = Medication.objects.create(
            name='Flucytosine',
            strength=500,
            units='mg',
            route='30',
            formulation='12')
        self.dosage_guideline = DosageGuideline.objects.create(
            medication_name='Flucytosine',
            dose_per_kg=100,
            dose_units='mg',
            dose_frequency_factor=1,
            dose_frequency_units='per_day',
            subject_weight_factor=1)
        self.prescription = Prescription.objects.create(
            subject_identifier=self.subject_identifier,
            weight_in_kgs=40,
            report_datetime=get_utcnow())

    def test_prescription_item_duration(self):
        obj = PrescriptionItem.objects.create(
            prescription=self.prescription,
            medication=self.medication,
            dosage_guideline=self.dosage_guideline,
            frequency=1,
            start_date=get_utcnow(),
            end_date=get_utcnow() + relativedelta(days=10))
        self.assertEqual(obj.rduration.days, 10)

    def test_prescription_str(self):
        obj = PrescriptionItem.objects.create(
            prescription=self.prescription,
            medication=self.medication,
            dosage_guideline=self.dosage_guideline,
            frequency=1,
            start_date=get_utcnow(),
            end_date=get_utcnow() + relativedelta(days=10))
        self.assertTrue(str(obj))

    def test_prescription_accepts_explicit_dose(self):
        obj = PrescriptionItem.objects.create(
            prescription=self.prescription,
            medication=self.medication,
            dosage_guideline=self.dosage_guideline,
            frequency=1,
            dose=3,
            start_date=get_utcnow(),
            end_date=get_utcnow() + relativedelta(days=10))
        self.assertEqual(obj.dose, 3)

    def test_prescription_calculates_dose(self):
        obj = PrescriptionItem.objects.create(
            prescription=self.prescription,
            medication=self.medication,
            dosage_guideline=self.dosage_guideline,
            frequency=1,
            dose=None,
            start_date=get_utcnow(),
            end_date=get_utcnow() + relativedelta(days=10))
        self.assertEqual(obj.dose, 8.0)
        self.assertEqual(obj.medication.units, 'mg')

    def test_prescription_total(self):
        obj = PrescriptionItem.objects.create(
            prescription=self.prescription,
            medication=self.medication,
            dosage_guideline=self.dosage_guideline,
            frequency=1,
            dose=None,
            start_date=get_utcnow(),
            end_date=get_utcnow() + relativedelta(days=7))
        self.assertEqual(obj.total, 56)

    def test_dispense(self):
        prescription_item = PrescriptionItem.objects.create(
            prescription=self.prescription,
            medication=self.medication,
            dosage_guideline=self.dosage_guideline,
            frequency=1,
            dose=None,
            start_date=get_utcnow(),
            end_date=get_utcnow() + relativedelta(days=7))
        obj = DispensedItem.objects.create(
            prescription=self.prescription,
            prescription_item=prescription_item,
            dispensed=8)
        self.assertEqual(obj.dispensed, 8)
        prescription_item = PrescriptionItem.objects.get(
            id=prescription_item.id)
        self.assertEqual(prescription_item.remaining, 56 - 8)

    def test_dispense_many(self):
        prescription_item = PrescriptionItem.objects.create(
            prescription=self.prescription,
            medication=self.medication,
            dosage_guideline=self.dosage_guideline,
            frequency=1,
            dose=None,
            start_date=get_utcnow(),
            end_date=get_utcnow() + relativedelta(days=7))
        dispensed = 0
        for amount in [8, 8, 8]:
            dispensed += amount
            obj = DispensedItem.objects.create(
                prescription=self.prescription,
                prescription_item=prescription_item,
                dispensed=8)
            self.assertEqual(obj.dispensed, 8)
            prescription_item = PrescriptionItem.objects.get(
                id=prescription_item.id)
            self.assertEqual(prescription_item.remaining, 56 - dispensed)

    def test_attempt_to_over_dispense(self):
        prescription_item = PrescriptionItem.objects.create(
            prescription=self.prescription,
            medication=self.medication,
            dosage_guideline=self.dosage_guideline,
            frequency=1,
            dose=None,
            start_date=get_utcnow(),
            end_date=get_utcnow() + relativedelta(days=7))
        dispensed = 0
        for amount in [8, 8, 8, 8, 8, 8, 8]:
            dispensed += amount
            obj = DispensedItem.objects.create(
                prescription=self.prescription,
                prescription_item=prescription_item,
                dispensed=8)
            self.assertEqual(obj.dispensed, 8)
            prescription_item = PrescriptionItem.objects.get(
                id=prescription_item.id)
            self.assertEqual(prescription_item.remaining, 56 - dispensed)
        prescription_item = PrescriptionItem.objects.get(
            id=prescription_item.id)
        self.assertEqual(prescription_item.remaining, 0)
        self.assertRaises(
            DispenseError,
            DispensedItem.objects.create,
            prescription=self.prescription,
            prescription_item=prescription_item,
            dispensed=8)
