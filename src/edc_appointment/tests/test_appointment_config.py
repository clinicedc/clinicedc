from django.test import TestCase, tag

from ..appointment_config import AppointmentConfig
from ..models import Appointment
from .models import SubjectVisit


class TestAppointmentConfig(TestCase):

    def test_appointment_model(self):
        appt_config = AppointmentConfig(
            model='edc_appointment.appointment',
            related_visit_model='edc_appointment.subjectvisit')
        self.assertEqual(Appointment, appt_config.model_cls)

    def test_appointment_related_model(self):
        appt_config = AppointmentConfig(
            model='edc_appointment.appointment',
            related_visit_model='edc_appointment.subjectvisit')
        self.assertEqual(SubjectVisit, appt_config.related_visit_model_cls)

    def test_appointment_related_model_as_class_raises(self):
        self.assertRaises(
            AttributeError,
            AppointmentConfig,
            model='edc_appointment.appointment',
            related_visit_model=SubjectVisit)
