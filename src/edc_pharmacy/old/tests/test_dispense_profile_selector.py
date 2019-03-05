from datetime import datetime, date

from django.test import TestCase, tag

from ..dispense_plan import dispense_plan_control
from ..models import DispenseSchedule, Appointment
from ..print_profile import DispenseProfileSelector


class RandomizedSubjectDummy:
    def __init__(self, randomization_datetime=None, subject_identifier=None):
        self.randomization_datetime = randomization_datetime or datetime.today()
        self.subject_identifier = subject_identifier


class TestDispenseProfileSelector(TestCase):
    def setUp(self):
        self.enrolled_subject = RandomizedSubjectDummy(
            randomization_datetime=datetime(2017, 8, 24), subject_identifier="1111"
        )
        self.schedule = DispenseSchedule.objects.create(
            subject_identifier=self.enrolled_subject.subject_identifier,
            name="schedule1",
            sequence=1,
            duration="2",
            start_datetime=date(2017, 9, 25),
            end_datetime=date(2017, 9, 30),
        )
        self.appointments = Appointment.objects.create(
            appt_datetime=datetime.today(),
            schedule=self.schedule,
            profile_label="enrollment.control",
        )

    def test_schedule_subject_selector(self):
        """Assert that first schedule (enrollment timepoint) returns enrollment
        dispense profile."""
        schedule_name = self.schedule.name
        self.appointments.delete()
        self.schedule.delete()
        dispense_selector = DispenseProfileSelector(
            subject_identifier=self.enrolled_subject.subject_identifier,
            schedule_name=schedule_name,
            schedule_plan=dispense_plan_control.get(schedule_name),
        )
        self.assertTrue(dispense_selector.profile)
        self.assertEqual(dispense_selector.profile.name, "enrollment")

    def test_schedule_subject_selector1(self):
        """Assert that first schedule (enrollment timepoint) returns enrollment
        dispense profile."""
        dispense_selector = DispenseProfileSelector(
            subject_identifier=self.enrolled_subject.subject_identifier,
            schedule_name=self.schedule.name,
            schedule_plan=dispense_plan_control.get(self.schedule.name),
        )
        self.assertTrue(dispense_selector.profile)
        self.assertEqual(dispense_selector.profile.name, "followup")
