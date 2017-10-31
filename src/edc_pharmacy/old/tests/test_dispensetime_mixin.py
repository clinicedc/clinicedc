from datetime import datetime, date
from edc_pharma.models import DispenseAppointment

from django.test import tag, TestCase

from ..constants import WEEKS
from ..print_profile import site_profiles
from ..scheduler import Scheduler


class RandomizedSubjectDummy:

    def __init__(self, randomization_datetime=None, subject_identifier=None):
        self.randomization_datetime = randomization_datetime or datetime.today()
        self.subject_identifier = subject_identifier


@tag('dispensetimemixin')
class TestDispenseAppointmentMixin(TestCase):

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
        self.randomized_subject = RandomizedSubjectDummy(
            randomization_datetime=datetime(2017, 8, 24),
            subject_identifier='1111')
        dispense = Scheduler(
            subject_identifier=self.randomized_subject.subject_identifier,
            dispense_plan=self.dispense_plan,
            arm='control')
        dispense.create_schedules()

    def test_dispensetime_next(self):
        dispense_timepoint = DispenseAppointment.objects.filter(
            schedule__subject_identifier=self.randomized_subject.subject_identifier
        ).order_by('created').first()
        self.assertEqual(dispense_timepoint.next(
        ).appt_datetime.date(), date(2017, 9, 1))

    def test_dispensetime_next_1(self):
        dispense_timepoint = DispenseAppointment.objects.filter(
            schedule__subject_identifier=self.randomized_subject.subject_identifier
        ).order_by('created').first()
        dispense_timepoint = dispense_timepoint.next()
        dispense_timepoint = dispense_timepoint.next()
        self.assertIsNone(dispense_timepoint)

    def test_dispensetime_previous(self):
        dispense_timepoint = DispenseAppointment.objects.filter(
            schedule__subject_identifier=self.randomized_subject.subject_identifier
        ).order_by('created').first()
        self.assertIsNone(dispense_timepoint.previous())

    def test_dispensetime_next_2(self):
        dispense_timepoint = DispenseAppointment.objects.filter(
            schedule__subject_identifier=self.randomized_subject.subject_identifier
        ).order_by('created').first()
        self.assertIsNone(dispense_timepoint.previous())
