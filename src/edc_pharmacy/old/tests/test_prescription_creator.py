from datetime import datetime

from django.test import TestCase, tag

from ..constants import WEEKS
from ..dispense.prescription_creator import PrescriptionCreator
from ..models import Appointment, Prescription
from ..print_profile import site_profiles
from ..scheduler import Scheduler


class RandomizedSubjectDummy:
    def __init__(self, randomization_datetime=None, subject_identifier=None):
        self.randomization_datetime = randomization_datetime or datetime.today()
        self.subject_identifier = subject_identifier


@tag("prescription")
class TestPrescriptionCreator(TestCase):
    def setUp(self):
        self.dispense_plan = {
            "schedule1": {
                "number_of_visits": 2,
                "duration": 2,
                "unit": WEEKS,
                "dispense_profile": {
                    "enrollment": site_profiles.get(name="enrollment.control"),
                    "followup": site_profiles.get(name="followup.control"),
                },
            },
            "schedule2": {
                "number_of_visits": 2,
                "duration": 8,
                "unit": WEEKS,
                "dispense_profile": {
                    "enrollment": site_profiles.get(name="enrollment.control"),
                    "followup": site_profiles.get(name="followup.control"),
                },
            },
        }
        self.options = {"weight": 40.0, "duration": 7}
        self.randomized_subject = RandomizedSubjectDummy(
            randomization_datetime=datetime(2017, 8, 24), subject_identifier="1111"
        )
        Scheduler(
            subject_identifier=self.randomized_subject.subject_identifier,
            dispense_plan=self.dispense_plan,
            randomization_datetime=self.randomized_subject.randomization_datetime,
            arm="control",
        )

    def test_dispense_history_creator(self):
        appointment = Appointment.objects.filter(
            schedule__subject_identifier=self.randomized_subject.subject_identifier
        ).first()
        PrescriptionCreator(appointment=appointment, options=self.options)
        self.assertEqual(
            Prescription.objects.filter(appointment=appointment).count(), 2
        )

    def test_dispense_history_creator_2(self):
        appointment = Appointment.objects.filter(
            schedule__subject_identifier=self.randomized_subject.subject_identifier
        ).first()
        PrescriptionCreator(appointment=appointment, options=self.options)
        appointment = Appointment.objects.filter(
            schedule__subject_identifier=self.randomized_subject.subject_identifier,
            is_dispensed=False,
        )
        self.assertEqual(appointment.count(), 4)

    def test_dispense_history_creator_3(self):
        appointment = (
            Appointment.objects.filter(
                schedule__subject_identifier=self.randomized_subject.subject_identifier
            )
            .order_by("created")
            .first()
        )
        PrescriptionCreator(appointment=appointment, options=self.options)
        appointment = appointment.next()
        PrescriptionCreator(appointment=appointment, options=self.options)
        appointment = Appointment.objects.filter(
            schedule__subject_identifier=self.randomized_subject.subject_identifier
        )
        self.assertEqual(
            Prescription.objects.filter(appointment=appointment).count(), 2
        )
        self.assertEqual(
            Prescription.objects.filter(
                appointment__schedule__subject_identifier=self.randomized_subject.subject_identifier
            ).count(),
            4,
        )

    def test_prescription_creator_initials(self):
        self.options.update({"clinician_initials": "TT", "initials": "CC"})
        appointment = (
            Appointment.objects.filter(
                schedule__subject_identifier=self.randomized_subject.subject_identifier
            )
            .order_by("created")
            .first()
        )
        PrescriptionCreator(appointment=appointment, options=self.options)
        appointment = appointment.next()
        PrescriptionCreator(appointment=appointment, options=self.options)
        appointment = Appointment.objects.filter(
            schedule__subject_identifier=self.randomized_subject.subject_identifier
        )
        self.assertEqual(
            Prescription.objects.filter(appointment=appointment).count(), 2
        )
        self.assertEqual(
            Prescription.objects.filter(
                appointment__schedule__subject_identifier=self.randomized_subject.subject_identifier
            ).count(),
            4,
        )

    def test_prescription_on_recommand_result(self):
        self.options.update({"clinician_initials": "TT", "initials": "CC"})
        appointment = (
            Appointment.objects.filter(
                schedule__subject_identifier=self.randomized_subject.subject_identifier
            )
            .order_by("created")
            .first()
        )
        PrescriptionCreator(appointment=appointment, options=self.options)
        prescription = Prescription.objects.all().order_by("created").first()
        self.assertEqual(prescription.result, 7)
        prescription.recommand_result = 10
        prescription.duration = 8
        prescription.save()
        self.assertEqual(prescription.result, 7)
