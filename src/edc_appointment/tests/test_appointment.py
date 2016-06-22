from datetime import date
from dateutil.relativedelta import relativedelta

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from edc_appointment.models import AppointmentMixin, AppointmentModelMixin, TimePointStatus
from edc_appointment.choices import APPT_STATUS
from edc_constants.constants import (
        NEW_APPT, COMPLETE_APPT, INCOMPLETE, CANCELLED, MALE, YES, SCHEDULED, IN_PROGRESS, DONE)
from edc_testing.tests.factories import TestConsentWithMixinFactory
from edc_testing.models.test_visit import TestVisit
from edc_visit_schedule.models.visit_definition import VisitDefinition

from .base_test_case import BaseTestCase


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

    APPOINTMENT_MODEL = AppointmentTestModel
    
    class Meta:
        app_label = 'edc_appointment'

    registered_subject = models.ForeignKey(RegisteredSubject)

    report_datetime = models.DateTimeField(default=timezone.now())

    def subject_registration_instance(self):
        """Returns the subject registration instance.

        Overide this method at the APPOINTMENT_MODEL"""
        return None

    class Meta:
        app_label = 'edc_appointment'


class TestAppointment(BaseTestCase):

    def test_create_appointment(self):
        appointment = AppointmentTestModel.objects.create(
            appt_datetime=timezone.now(),
            visit_definition=self.visit_definition)
        with self.assertRaises(TimePointStatus.DoesNotExist):
            try:
                TimePointStatus.objects.get(appointment=appointment)
            except:
                pass
            else:
                raise TimePointStatus.DoesNotExist

#     def test_create_continuation_appointment(self):
#         """Asserts continuation appointment datetime is at least 1 day greater than the previous."""
#         appointment = Appointment.objects.create(
#             registered_subject=self.registered_subject,
#             appt_datetime=timezone.now(),
#             visit_definition=self.visit_definition)
#         continuation_appt = Appointment.objects.create(
#             registered_subject=self.registered_subject,
#             appt_datetime=timezone.now() + relativedelta(days=5),
#             visit_definition=self.visit_definition,
#             visit_instance='1')
#         self.assertGreaterEqual((continuation_appt.appt_datetime - appointment.appt_datetime).days, 1)
# 
#     def test_create_continuation_appointment_not_future_date(self):
#         """Asserts continuation appointment datetime is at least 1 day greater than the previous."""
#         Appointment.objects.create(
#             registered_subject=self.registered_subject,
#             appt_datetime=timezone.now(),
#             visit_definition=self.visit_definition)
#         self.assertRaises(
#             ValidationError,
#             Appointment.objects.create,
#             registered_subject=self.registered_subject,
#             appt_datetime=timezone.now(),
#             visit_definition=self.visit_definition,
#             visit_instance='1')
# 
#     def test_delete_appointment(self):
#         """Asserts that appointment can be deleted.
# 
#         Note TimepointStatus must be deleted first."""
#         appointment = Appointment.objects.create(
#             registered_subject=self.registered_subject,
#             appt_datetime=timezone.now(),
#             visit_definition=self.visit_definition)
#         appointment.delete()
# 
#     def test_appointment_visit_instance_default(self):
#         appointment = Appointment.objects.create(
#             registered_subject=self.registered_subject,
#             appt_datetime=timezone.now(),
#             visit_definition=self.visit_definition)
#         self.assertEqual(appointment.visit_instance, '0')
# 
#     def test_appointment_visit_instance_unchanged(self):
#         appointment = Appointment.objects.create(
#             registered_subject=self.registered_subject,
#             appt_datetime=timezone.now(),
#             visit_definition=self.visit_definition)
#         appointment.save()
#         self.assertEqual(appointment.visit_instance, '0')
# 
#     def test_appointment_visit_instance_change(self):
#         """Asserts that the visit instance cannot be incremented out of sequence."""
#         appointment = Appointment.objects.create(
#             registered_subject=self.registered_subject,
#             appt_datetime=timezone.now(),
#             visit_definition=self.visit_definition)
#         self.assertEqual(appointment.visit_instance, '0')
#         appointment.visit_instance = '1'
#         self.assertRaises(ValidationError, appointment.save)
# 
#     def test_appointment_visit_instance_change2(self):
#         """Asserts that the visit instance cannot be incremented out of sequence."""
#         appointment = Appointment.objects.create(
#             registered_subject=self.registered_subject,
#             appt_datetime=timezone.now() - relativedelta(weeks=1),
#             visit_definition=self.visit_definition)
#         self.assertEqual(appointment.visit_instance, '0')
#         self.assertRaises(
#             ValidationError,
#             Appointment.objects.create,
#             appt_datetime=timezone.now(),
#             visit_definition=self.visit_definition,
#             registered_subject=self.registered_subject,
#             visit_instance='2')
# 
#     def test_is_new_appointment(self):
#         """Assert is_new_appointment() should return False if not "new"."""
#         appointment = Appointment.objects.create(
#             registered_subject=self.registered_subject,
#             appt_datetime=timezone.now(),
#             visit_definition=self.visit_definition)
#         self.assertEqual(appointment.appt_status, NEW_APPT)
#         self.assertTrue(appointment.is_new_appointment())
#         TestVisit.objects.create(
#             appointment=appointment, reason=SCHEDULED, report_datetime=timezone.now())
#         appointment.appt_status = COMPLETE_APPT
#         appointment.save()
#         self.assertFalse(appointment.is_new_appointment())
#         appointment.appt_status = INCOMPLETE
#         appointment.save()
#         self.assertFalse(appointment.is_new_appointment())
#         appointment.appt_status = CANCELLED
#         appointment.save()
#         self.assertFalse(appointment.is_new_appointment())
# 
#     def test_creates_appointments(self):
#         TestConsentWithMixinFactory(
#             registered_subject=self.registered_subject,
#             consent_datetime=timezone.now(),
#             gender=MALE,
#             is_literate=YES,
#             dob=date.today() - relativedelta(years=35),
#             identity='111111111',
#             confirm_identity='111111111',
#             subject_identifier='999-100000-1',
#             study_site=self.study_site)
#         self.assertEquals(Appointment.objects.all().count(), 2)
# 
#     def test_appt_status_change_requires_visit_unless_cancelled(self):
#         TestConsentWithMixinFactory(
#             registered_subject=self.registered_subject,
#             consent_datetime=timezone.now(),
#             gender=MALE,
#             is_literate=YES,
#             dob=date.today() - relativedelta(years=35),
#             identity='111111111',
#             confirm_identity='111111111',
#             subject_identifier='999-100000-1',
#             study_site=self.study_site)
#         self.assertEquals(Appointment.objects.all().count(), 2)
#         for appointment in Appointment.objects.all():
#             for appt_status in [x[0] for x in APPT_STATUS]:
#                 appointment.appt_status = appt_status
#                 appointment.save()
#                 if appt_status == CANCELLED:
#                     self.assertEqual(appointment.appt_status, CANCELLED)
#                 else:
#                     self.assertEqual(appointment.appt_status, NEW_APPT)
# 
#     def test_appt_status_in_progress_on_visit(self):
#         TestConsentWithMixinFactory(
#             registered_subject=self.registered_subject,
#             consent_datetime=timezone.now(),
#             gender=MALE,
#             is_literate=YES,
#             dob=date.today() - relativedelta(years=35),
#             identity='111111111',
#             confirm_identity='111111111',
#             subject_identifier='999-100000-1',
#             study_site=self.study_site)
#         visit_definition = VisitDefinition.objects.get(code='1000')
#         appointment = Appointment.objects.get(
#             registered_subject=self.registered_subject,
#             visit_definition=visit_definition)
#         TestVisit.objects.create(
#             appointment=appointment, reason=SCHEDULED, report_datetime=timezone.now())
#         self.assertEquals(appointment.appt_status, IN_PROGRESS)
# 
#     def test_in_progress_unless_cancelled_or_incomplete(self):
#         TestConsentWithMixinFactory(
#             registered_subject=self.registered_subject,
#             consent_datetime=timezone.now(),
#             gender=MALE,
#             is_literate=YES,
#             dob=date.today() - relativedelta(years=35),
#             identity='111111111',
#             confirm_identity='111111111',
#             subject_identifier='999-100000-1',
#             study_site=self.study_site)
#         visit_definition = VisitDefinition.objects.get(code='1000')
#         appointment = Appointment.objects.get(
#             registered_subject=self.registered_subject,
#             visit_definition=visit_definition)
#         TestVisit.objects.create(
#             appointment=appointment, reason=SCHEDULED, report_datetime=timezone.now())
#         for appt_status in [x[0] for x in APPT_STATUS]:
#             appointment.appt_status = appt_status
#             appointment.save()
#             appointment = Appointment.objects.get(pk=appointment.pk)
#             if appt_status == INCOMPLETE:
#                 self.assertEquals(appointment.appt_status, INCOMPLETE)
#             elif appt_status == DONE:
#                 self.assertEquals(appointment.appt_status, INCOMPLETE)
#             elif appt_status == CANCELLED:
#                 self.assertEquals(appointment.appt_status, IN_PROGRESS)
#             else:
#                 self.assertEquals(appointment.appt_status, IN_PROGRESS)
# 
#     def test_validate_appt_datetimes_equal(self):
#         """Assert appointment.appt_datetime and best_appt_datetime are equal for a new appt."""
#         appointment = Appointment.objects.create(
#             registered_subject=self.registered_subject,
#             appt_datetime=timezone.now(),
#             visit_definition=self.visit_definition)
#         appt_datetime, best_appt_datetime = appointment.validate_appt_datetime()
#         self.assertEqual(appt_datetime, best_appt_datetime)
# 
#     def test_timepoint_status(self):
#         """Assert a timepoint status instance is created for every appointment."""
#         for appointment in Appointment.objects.all():
#             self.assertTrue(appointment.time_point_status)
# 
#     def test_timepoint_status_for_visit(self):
#         """Assert only one timepoint status instance is created for a visit code."""
#         TestConsentWithMixinFactory(
#             registered_subject=self.registered_subject,
#             consent_datetime=timezone.now(),
#             gender=MALE,
#             is_literate=YES,
#             dob=date.today() - relativedelta(years=35),
#             identity='111111111',
#             confirm_identity='111111111',
#             subject_identifier='999-100000-1',
#             study_site=self.study_site)
#         visit_definition = VisitDefinition.objects.get(code='1000')
#         appointment = Appointment.objects.get(
#             registered_subject=self.registered_subject,
#             visit_definition=visit_definition)
#         self.assertTrue(appointment.time_point_status)
#         time_point_status = appointment.time_point_status
#         appointment = Appointment.objects.create(
#             registered_subject=self.registered_subject,
#             appt_datetime=timezone.now() + relativedelta(days=1),
#             visit_definition=self.visit_definition,
#             visit_instance='1')
#         self.assertEqual(appointment.time_point_status, time_point_status)
#         appointment = Appointment.objects.create(
#             registered_subject=self.registered_subject,
#             appt_datetime=timezone.now() + relativedelta(days=2),
#             visit_definition=self.visit_definition,
#             visit_instance='2')
#         self.assertEqual(appointment.time_point_status, time_point_status)


class AppointmentModelMixin(models.Model):
    is_confirmed = models.BooleanField(default=False, editable=False)
    def p_isconfirmed(self):
        for ap in self.__class__.objects.all():
            print "Is confirmed value", ap.is_confirmed
    class Meta:
        abstract = True
        
class AppointmentTestModel(AppointmentModelMixin, models.Model):
    class Meta:
       app_label = 'edc_appointment' 