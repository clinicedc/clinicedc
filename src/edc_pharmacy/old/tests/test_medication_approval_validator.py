from datetime import datetime
from edc_pharma.dispense import PrescriptionCreator
from edc_pharma.medications import PrescriptionApprovalValidator
from edc_pharma.models.prescription import Prescription

from django.test import TestCase, tag

from ..constants import WEEKS
from ..medications.prescription_approval_validator import PrescriptionApprovalValidatorError
from ..print_profile import site_profiles
from ..scheduler import Scheduler


class RandomizedSubjectDummy:

    def __init__(self, randomization_datetime=None, subject_identifier=None):
        self.randomization_datetime = randomization_datetime or datetime.today()
        self.subject_identifier = subject_identifier


@tag('Validator')
class TestMedicationApprovalValidator(TestCase):

    def setUp(self):
        self.options = {'weight': 40.0, 'duration': 7}
        self.dispense_plan = {
            'schedule1': {
                'number_of_visits': 2, 'duration': 2, 'unit': WEEKS,
                'dispense_profile': {
                    'enrollment': site_profiles.get(name='enrollment.control'),
                    'followup': site_profiles.get(name='followup.control'),
                }},
            'schedule2': {
                'number_of_visits': 2, 'duration': 8, 'unit': WEEKS,
                'dispense_profile': {
                    'enrollment': site_profiles.get(name='enrollment.control'),
                    'followup': site_profiles.get(name='followup.control'),
                }}}
        self.randomized_subject = RandomizedSubjectDummy(
            randomization_datetime=datetime(2017, 8, 24),
            subject_identifier='1111')
        self.scheduler = Scheduler(
            subject_identifier=self.randomized_subject.subject_identifier,
            randomization_datetime=self.randomized_subject.randomization_datetime,
            dispense_plan=self.dispense_plan,
            arm='control')

    def test_validator(self):
        appointment = self.scheduler.dispense_appointments[0]
        prescriptions = Prescription.objects.filter(
            dispense_appointment=appointment)
        PrescriptionCreator(
            dispense_appointment=appointment, options=self.options)
        self.assertEqual(Prescription.objects.filter(
            dispense_appointment=appointment).count(), 2)
        self.assertEqual(prescriptions.count(), 2)
        for p in prescriptions:
            p.is_approved = True
            p.save()

        prescriptions = Prescription.objects.filter(
            dispense_appointment=appointment, is_approved=True)
        self.assertEqual(prescriptions.count(), 2)

    def test_validator_1(self):
        appointment = self.scheduler.dispense_appointments[0]
        prescriptions = Prescription.objects.filter(
            dispense_appointment=appointment)
        PrescriptionCreator(
            dispense_appointment=appointment, options=self.options)
        self.assertEqual(Prescription.objects.filter(
            dispense_appointment=appointment).count(), 2)
        self.assertEqual(prescriptions.count(), 2)
        for p in prescriptions:
            p.is_approved = True
            p.save()
        appointment = self.scheduler.dispense_appointments[1]
        prescriptions = Prescription.objects.filter(
            dispense_appointment=appointment)
        PrescriptionCreator(
            dispense_appointment=appointment, options=self.options)
        PrescriptionApprovalValidator(prescriptions=prescriptions)
        for p in prescriptions:
            p.is_approved = True
            p.save()
        prescriptions = Prescription.objects.filter(
            dispense_appointment=appointment)
        self.assertEqual(prescriptions.filter(is_approved=True).count(), 2)

    def test_validator_2(self):
        appointment = self.scheduler.dispense_appointments[0]
        prescriptions = Prescription.objects.filter(
            dispense_appointment=appointment)
        PrescriptionCreator(
            dispense_appointment=appointment, options=self.options)
        self.assertEqual(Prescription.objects.filter(
            dispense_appointment=appointment).count(), 2)
        self.assertEqual(prescriptions.count(), 2)
        for p in prescriptions:
            p.is_approved = False
            p.save()
        appointment = self.scheduler.dispense_appointments[1]
        prescriptions = Prescription.objects.filter(
            dispense_appointment=appointment)
        PrescriptionCreator(
            dispense_appointment=appointment, options=self.options)
        self.assertRaises(PrescriptionApprovalValidatorError,
                          PrescriptionApprovalValidator, prescriptions=prescriptions)
