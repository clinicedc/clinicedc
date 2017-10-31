from datetime import datetime

from django.test import tag, TestCase

from ..constants import WEEKS
from ..dispense.labels import DispenseLabelContext
from ..models import DispenseAppointment
from ..print_profile import site_profiles
from ..scheduler import Scheduler


class RandomizedSubjectDummy:

    def __init__(self, randomization_datetime=None, subject_identifier=None):
        self.randomization_datetime = randomization_datetime or datetime.today()
        self.subject_identifier = subject_identifier


@tag('dispense_context')
class TestDispenseContext(TestCase):

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

    def test_context_list_control(self):
        """Assert that calculated subject_schedules equals
        number of specified in a plan."""
        randomized_subject = RandomizedSubjectDummy(
            randomization_datetime=datetime(2017, 8, 24),
            subject_identifier='1111')
        Scheduler(
            subject_identifier=randomized_subject.subject_identifier,
            dispense_plan=self.dispense_plan,
            arm='control')
        dispense_appointment = DispenseAppointment.objects.filter(
            schedule__subject_identifier=randomized_subject.subject_identifier
        ).order_by('created').first()
        context = DispenseLabelContext(
            dispense_appointment=dispense_appointment)
        self.assertEqual(len(context.context_list), 2)
