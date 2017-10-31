from datetime import datetime
from edc_pharma import AppointmentDescriber

from django.test import tag, TestCase

from ..constants import WEEKS
from ..models import DispenseAppointment
from ..print_profile import site_profiles
from ..scheduler import Scheduler


class RandomizedSubjectDummy:

    def __init__(self, randomization_datetime=None, subject_identifier=None):
        self.randomization_datetime = randomization_datetime or datetime.today()
        self.subject_identifier = subject_identifier


class TestDispenseAppointmentDescribe(TestCase):

    def setUp(self):
        self.dispense_plan = {
            'schedule1': {
                'number_of_visits': 2, 'duration': 2, 'unit': WEEKS,
                'description': 'Enrollment',
                'dispense_profile': {
                    'enrollment': site_profiles.get(name='enrollment.control'),
                    'followup': site_profiles.get(name='followup.control'),
                }},
            'schedule2': {
                'number_of_visits': 2, 'duration': 8, 'unit': WEEKS,
                'description': 'Followup',
                'dispense_profile': {
                    'enrollment': site_profiles.get(name='enrollment.control'),
                    'followup': site_profiles.get(name='followup.control'),
                }}}
        self.randomized_subject = RandomizedSubjectDummy(
            randomization_datetime=datetime(2017, 8, 24),
            subject_identifier='1111')
        Scheduler(
            subject_identifier=self.randomized_subject.subject_identifier,
            dispense_plan=self.dispense_plan,
            arm='control_arm')

    def test_dispense_appointment_start_day(self):
        dispense_appointment = DispenseAppointment.objects.filter(
            schedule__subject_identifier=self.randomized_subject.subject_identifier,
            is_dispensed=False
        ).order_by('created').first()
        describe = AppointmentDescriber(
            dispense_appointment=dispense_appointment)
        self.assertTrue(describe.human_readiable())
        self.assertEqual('Day 1', describe.start_day)

    @tag('readiable_days_7')
    def test_dispense_appointment_human_readiable_days_7(self):
        dispense_appointment = DispenseAppointment.objects.filter(
            schedule__subject_identifier=self.randomized_subject.subject_identifier,
            is_dispensed=False
        ).order_by('created').first()
        dispense_appointment = dispense_appointment.next()
        appt_describe = AppointmentDescriber(
            dispense_appointment=dispense_appointment)
        self.assertTrue(appt_describe.human_readiable())
        self.assertIn('Day 8', appt_describe.start_day)
        self.assertEqual('Day 14', appt_describe.end_day)

    def test_dispense_appointment_human_readiable_days_3(self):
        dispense_appointment = DispenseAppointment.objects.filter(
            schedule__subject_identifier=self.randomized_subject.subject_identifier,
            is_dispensed=False
        ).order_by('created').first()
        appt_describe = AppointmentDescriber(
            dispense_appointment=dispense_appointment)
        self.assertTrue(appt_describe.human_readiable())
        self.assertEqual('Day 1', appt_describe.start_day)
        self.assertEqual('Day 7', appt_describe.end_day)

    def test_dispense_appointment_human_readiable_days(self):
        dispense_appointment = DispenseAppointment.objects.filter(
            schedule__subject_identifier=self.randomized_subject.subject_identifier,
            is_dispensed=False
        ).order_by('created').first()
        appt_describe = AppointmentDescriber(
            dispense_appointment=dispense_appointment)
        self.assertTrue(appt_describe.human_readiable())
        self.assertIn('Day 1', appt_describe.human_readiable())
        self.assertIn('Day 7', appt_describe.human_readiable())

    def test_dispense_appointment_human_readiable_days_1(self):
        dispense_appointment = DispenseAppointment.objects.filter(
            schedule__subject_identifier=self.randomized_subject.subject_identifier,
            is_dispensed=False
        ).order_by('created').first()
        dispense_appointment = dispense_appointment.next()
        appt_describe = AppointmentDescriber(
            dispense_appointment=dispense_appointment)
        self.assertTrue(appt_describe.human_readiable())
        self.assertIn('Day 8', appt_describe.human_readiable())
        self.assertIn('Day 14', appt_describe.human_readiable())

    def test_is_next_pending_appointment(self):
        dispense_appointment = DispenseAppointment.objects.filter(
            schedule__subject_identifier=self.randomized_subject.subject_identifier,
            is_dispensed=False
        ).order_by('created').first()
        describe = AppointmentDescriber(
            dispense_appointment=dispense_appointment)
        self.assertTrue(describe.is_next_pending_appointment())

    @tag('descriptor')
    def test_is_next_pending_appointment_1(self):
        dispense_appointment = DispenseAppointment.objects.filter(
            schedule__subject_identifier=self.randomized_subject.subject_identifier,
            is_dispensed=False
        ).order_by('appt_datetime').first()
        dispense_appointment.is_dispensed = True
        dispense_appointment.save()
        dispense_appointment = dispense_appointment.next()
        describe = AppointmentDescriber(
            dispense_appointment=dispense_appointment)
        self.assertTrue(describe.is_next_pending_appointment())

    @tag('descriptor')
    def test_is_next_pending_appointment_2(self):
        dispense_appointment1 = DispenseAppointment.objects.filter(
            schedule__subject_identifier=self.randomized_subject.subject_identifier,
            is_dispensed=False
        ).order_by('appt_datetime').first()
        dispense_appointment1.is_dispensed = True
        dispense_appointment1.save()
        describe = AppointmentDescriber(
            dispense_appointment=dispense_appointment1)
        self.assertFalse(describe.is_next_pending_appointment())
