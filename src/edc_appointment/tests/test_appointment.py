from django.db import models
from django.utils import timezone
from django.test import TestCase

from edc_appointment.models import AppointmentMixin, AppointmentModelMixin

# from .base_test_case import BaseTestCase
from .test_visit_schedule import VisitSchedule


class RegisteredSubject(models.Model):

    subject_identifier = models.CharField(
        verbose_name="Subject Identifier",
        max_length=50,
        blank=True,
        db_index=True,
        unique=True)

    study_site = models.CharField(
        max_length=50,
        null=True,
        blank=True)

    class Meta:
        app_label = 'edc_appointment'


class AppointmentTestModel(AppointmentModelMixin, models.Model):

    registered_subject = models.ForeignKey(RegisteredSubject)

    report_datetime = models.DateTimeField(default=timezone.now())

    def subject_registration_instance(self):
        """Returns the subject registration instance.

        Overide this method at the APPOINTMENT_MODEL"""
        return self.registered_subject

    class Meta:
        app_label = 'edc_appointment'


class TestModel(AppointmentMixin):

    APPOINTMENT_MODEL = AppointmentTestModel

    def save(self, *args, **kwargs):
        self.prepare_appointments()
        super(TestModel, self).save(*args, **kwargs)

    class Meta:
        app_label = 'edc_appointment'


class TestAppointment(TestCase):

    def setUp(self):
        VisitSchedule().build()

    def test_appointments_creation(self):
        """Text if appoint trigering method creates appointment."""
        TestModel.objects.create()
#         self.assertEqual(AppointmentTestModel.objects.all().count(), 3)
