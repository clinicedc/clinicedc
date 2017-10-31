from datetime import datetime, date
from django.test import tag, TestCase

from ..constants import WEEKS
from ..models import DispenseSchedule, Appointment
from ..print_profile import site_profiles
from ..scheduler import Scheduler, InvalidScheduleConfig, SchedulerException


class RandomizedSubjectDummy:

    def __init__(self, randomization_datetime=None, subject_identifier=None):
        self.randomization_datetime = randomization_datetime or datetime.today()
        self.subject_identifier = subject_identifier


class TestDispensePlanScheduler(TestCase):

    def setUp(self):
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

    def test_schedule_subject(self):
        """Assert that calculated subject_schedules equals
        number of specified in a plan."""
        randomized_subject = RandomizedSubjectDummy(
            randomization_datetime=datetime(2017, 8, 24),
            subject_identifier='1111')
        dispense = Scheduler(
            subject_identifier=randomized_subject.subject_identifier,
            dispense_plan=self.dispense_plan,
            arm='control_arm')
        self.assertEqual(len(dispense.subject_schedules),
                         len(self.dispense_plan))

    def test_schedule_subject1(self):
        """Assert that calculated subject_schedules equals
        number of specified in a plan."""
        del self.dispense_plan['schedule2']
        randomized_subject = RandomizedSubjectDummy(
            randomization_datetime=datetime(2017, 8, 24),
            subject_identifier='1111')
        dispense = Scheduler(
            subject_identifier=randomized_subject.subject_identifier,
            dispense_plan=self.dispense_plan,
            randomization_datetime=randomized_subject.randomization_datetime,
            arm='control_arm')
        self.assertEqual(len(dispense.subject_schedules), 1)

    def test_schedule_subject_invalid_plan(self):
        """Assert that calculated subject_schedules equals
        number of specified in a plan."""
        invalid_dispense_plan = {
            'schedule1': {
                'number_of_visits': 2, 'duration': 2}
        }
        randomized_subject = RandomizedSubjectDummy(
            randomization_datetime=datetime(2017, 8, 24),
            subject_identifier='1111')

        self.assertRaises(
            InvalidScheduleConfig,
            Scheduler,
            subject_identifier=randomized_subject.subject_identifier,
            dispense_plan=invalid_dispense_plan,
            arm='control_arm')

    def test_last_schedule(self):
        """Assert that last schedule dates are calculated correctly."""
        randomized_subject = RandomizedSubjectDummy(
            randomization_datetime=datetime(2017, 8, 24), subject_identifier='1111')
        scheduler = Scheduler(
            subject_identifier=randomized_subject.subject_identifier,
            dispense_plan=self.dispense_plan,
            randomization_datetime=randomized_subject.randomization_datetime,
            arm='control_arm')
        last_schedule = scheduler.subject_schedules.last()
        self.assertEqual(
            last_schedule.period.start_datetime.date(), date(2017, 9, 8))
        self.assertEqual(
            last_schedule.period.end_datetime.date(), date(2017, 11, 3))

    def test_schedule_subject2(self):
        """Assert that all schedules are created successfully."""
        randomized_subject = RandomizedSubjectDummy(
            randomization_datetime=datetime(2017, 8, 24), subject_identifier='1111')
        Scheduler(
            subject_identifier=randomized_subject.subject_identifier,
            dispense_plan=self.dispense_plan,
            arm='control_arm')
        self.assertEqual(DispenseSchedule.objects.all().count(), 2)

    def test_schedule_subject3(self):
        randomized_subject = RandomizedSubjectDummy(
            randomization_datetime=datetime(2017, 8, 24),
            subject_identifier='1111')
        scheduler = Scheduler(
            subject_identifier=randomized_subject.subject_identifier,
            dispense_plan=self.dispense_plan,
            randomization_datetime=randomized_subject.randomization_datetime,
            arm='control_arm')
        schedule = DispenseSchedule.objects.all().first()
        self.assertEqual(
            Appointment.objects.filter(schedule=schedule).count(), 2)
        self.assertEqual(len(scheduler.appointments), 4)

    def test_schedule_subject4(self):
        randomized_subject = RandomizedSubjectDummy(
            randomization_datetime=datetime(2017, 8, 24),
            subject_identifier='1111')
        Scheduler(
            subject_identifier=randomized_subject.subject_identifier,
            dispense_plan=self.dispense_plan,
            randomization_datetime=randomized_subject.randomization_datetime,
            arm='control_arm')
        self.assertEqual(Appointment.objects.all().count(), 4)

    def test_schedule_subject6(self):
        for i in range(1, 5):
            randomized_subject = RandomizedSubjectDummy(
                randomization_datetime=datetime(2017, 8, 24),
                subject_identifier=f'111{i}')
            Scheduler(
                subject_identifier=randomized_subject.subject_identifier,
                dispense_plan=self.dispense_plan,
                arm='control_arm')
            self.assertEqual(Appointment.objects.all().count(), 4 * i)

    def test_schedule_subject7(self):
        for i in range(1, 5):
            randomized_subject = RandomizedSubjectDummy(
                randomization_datetime=datetime(2017, 8, 24),
                subject_identifier=f'111{i}')
            self.assertRaises(SchedulerException,
                              Scheduler,
                              subject_identifier=randomized_subject.subject_identifier,
                              arm='control_arm_wrong')

    def test_schedule_subject5(self):
        randomized_subject = RandomizedSubjectDummy(
            randomization_datetime=datetime(2017, 8, 24),
            subject_identifier='1111')
        Scheduler(
            subject_identifier=randomized_subject.subject_identifier,
            dispense_plan=self.dispense_plan,
            randomization_datetime=randomized_subject.randomization_datetime,
            arm='control_arm')
        schedule = DispenseSchedule.objects.all().order_by(
            'created').first()
        p1, p2 = Appointment.objects.filter(schedule=schedule)
        self.assertEqual(p1.appt_datetime.date(), date(2017, 8, 24))
        self.assertEqual(p2.appt_datetime.date(), date(2017, 9, 1))
