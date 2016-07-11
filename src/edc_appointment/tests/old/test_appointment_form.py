# from datetime import date
# from dateutil.relativedelta import relativedelta
# 
# from django import forms
# from django.db import models
# from django.utils import timezone
# 
# from edc_appointment.forms.appointment_form import AppointmentForm
# from edc_appointment.models import AppointmentMixin, Appointment
# from edc_appointment.tests.test_models import TestCrfModel1, TestCrfModel2, TestCrfModel3, TestRequisitionModel
# from edc_constants.constants import (
#     NEW_APPT, COMPLETE_APPT, MALE, YES, SCHEDULED, IN_PROGRESS)
# from edc_registration.models import RegisteredSubject
# from edc_testing.models.test_panel import TestPanel
# from edc_testing.models.test_aliquot_type import TestAliquotType
# from edc_testing.tests.factories import TestConsentWithMixinFactory
# from edc_testing.models.test_visit import TestVisit
# from edc_visit_schedule.models.visit_definition import VisitDefinition
# 
# 
# from .base_test_case import BaseTestCase
# from edc_appointment.models.time_point_status import TimePointStatus
# 
# 
# class TestRegistrationModel(AppointmentMixin, models.Model):
# 
#     registered_subject = models.ForeignKey(RegisteredSubject)
# 
#     report_datetime = models.DateTimeField(default=timezone.now())
# 
#     class Meta:
#         app_label = 'edc_appointment'
# 
# 
# class TestAppointmentForm(BaseTestCase):
# 
#     def setUp(self):
#         super(TestAppointmentForm, self).setUp()
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
#         self.appointment = Appointment.objects.get(
#             registered_subject=self.registered_subject,
#             visit_definition=visit_definition)
#         self.test_visit = TestVisit.objects.create(
#             appointment=self.appointment, reason=SCHEDULED, report_datetime=timezone.now())
#         self.panel = TestPanel.objects.first()
#         self.aliquot_type = TestAliquotType.objects.first()
# 
#     def test_form_appt_status_complete_with_unkeyed(self):
#         """Asserts appointment cannot be complete if unkeyed CRFs exists."""
#         form = AppointmentForm(
#             {'appt_status': COMPLETE_APPT,
#              'registered_subject': self.appointment.registered_subject.id},
#             instance=self.appointment)
#         self.assertFalse(form.is_valid())
#         self.assertIn(
#             'Appointment is not \'complete\'. Some CRFs are still required.',
#             form.errors.get('__all__'))
# 
#     def test_form_appt_status_complete2(self):
#         """Asserts appointment cannot be complete if unkeyed requisitions exists."""
#         TestCrfModel1.objects.create(test_visit=self.test_visit)
#         TestCrfModel2.objects.create(test_visit=self.test_visit)
#         TestCrfModel3.objects.create(test_visit=self.test_visit)
#         form = AppointmentForm(
#             {'appt_status': COMPLETE_APPT,
#              'registered_subject': self.appointment.registered_subject.id},
#             instance=self.appointment)
#         self.assertFalse(form.is_valid())
#         self.assertIn(
#             'Appointment is not \'complete\'. Some Requisitions are still required.',
#             form.errors.get('__all__'))
# 
#     def test_form_appt_status_new_keyed(self):
#         """Asserts that an appointment cannot new if keyed CRFs meta data exists."""
#         TestCrfModel1.objects.create(test_visit=self.test_visit)
#         form = AppointmentForm(
#             {'appt_status': NEW_APPT,
#              'registered_subject': self.appointment.registered_subject.id,
#              'appt_datetime': self.appointment.appt_datetime,
#              'appt_type': 'clinic',
#              'visit_definition': self.appointment.visit_definition.id},
#             instance=self.appointment)
#         self.assertFalse(form.is_valid())
#         self.assertIn(
#             'Appointment is not \'new\'. Some CRFs have been completed.',
#             form.errors.get('__all__') or [])
# 
#     def test_form_appt_status_new_keyed2(self):
#         """Asserts that an appointment cannot be new if keyed Requisition meta data exists."""
#         TestRequisitionModel.objects.create(
#             test_visit=self.test_visit,
#             panel=self.panel,
#             aliquot_type=self.aliquot_type)
#         form = AppointmentForm(
#             {'appt_status': NEW_APPT,
#              'registered_subject': self.appointment.registered_subject.id,
#              'appt_datetime': self.appointment.appt_datetime,
#              'appt_type': 'clinic',
#              'visit_definition': self.appointment.visit_definition.id},
#             instance=self.appointment)
#         self.assertTrue(self.appointment.visit_code_sequence == '0')
#         self.assertFalse(form.is_valid())
#         self.assertIn(
#             'Appointment is not \'new\'. Some Requisitions have been completed.',
#             form.errors.get('__all__') or [])
# 
#     def test_form_appt_status_in_progress_not_allowed(self):
#         """Asserts appointment cannot be in progress while another is already in progress."""
#         Appointment.objects.all().update(appt_status=NEW_APPT)
#         self.assertEqual(Appointment.objects.filter(appt_status=IN_PROGRESS).count(), 0)
#         self.appointment.appt_status = IN_PROGRESS
#         self.appointment.save()
#         visit_definition = VisitDefinition.objects.get(code='2000')
#         appointment = Appointment.objects.get(
#             registered_subject=self.registered_subject,
#             visit_definition=visit_definition)
#         form = AppointmentForm(
#             {'appt_status': IN_PROGRESS,
#              'registered_subject': appointment.registered_subject.id,
#              'appt_datetime': appointment.appt_datetime,
#              'appt_type': 'clinic',
#              'visit_definition': appointment.visit_definition.id},
#             instance=appointment)
#         self.assertFalse(form.is_valid())
#         self.assertIn(
#             'Another appointment is currently \'in progress\'. Only one appointment '
#             'may be in progress at a time. Please resolve before continuing.',
#             form.errors.get('__all__') or [])
# 
#     def test_form_appt_status_in_progress_allowed(self):
#         """Asserts appointment can be in progress if no others are."""
#         Appointment.objects.all().update(appt_status=NEW_APPT)
#         self.assertEqual(Appointment.objects.filter(appt_status=IN_PROGRESS).count(), 0)
#         form = AppointmentForm(
#             {'appt_status': IN_PROGRESS,
#              'registered_subject': self.appointment.registered_subject.id,
#              'appt_datetime': self.appointment.appt_datetime,
#              'appt_type': 'clinic',
#              'visit_definition': self.appointment.visit_definition.id},
#             instance=self.appointment)
#         self.assertTrue(form.is_valid())
# 
#     def test_form_appt_out_of_sequence(self):
#         """Asserts appointment visit instance must increment by more than 1."""
#         visit_code_sequences = []
#         for obj in Appointment.objects.filter(
#                 registered_subject=self.registered_subject,
#                 visit_definition=self.appointment.visit_definition):
#             visit_code_sequences.append(obj.visit_code_sequence)
#         self.assertEquals(visit_code_sequences, ['0'])
#         form = AppointmentForm(
#             {'appt_datetime': self.appointment.appt_datetime,
#              'appt_status': IN_PROGRESS,
#              'appt_type': 'clinic',
#              'registered_subject': self.appointment.registered_subject.id,
#              'visit_definition': self.appointment.visit_definition.id,
#              'visit_code_sequence': '5'},
#             instance=self.appointment)
#         self.assertFalse(form.is_valid())
#         self.assertIn(
#             'Attempt to create or update appointment instance out of sequence. Got \'1000.5\'.',
#             form.errors.get('__all__'))
# 
#     def test_form_appt_out_of_sequence2(self):
#         """Asserts appointment visit instance must increment by 1."""
#         visit_code_sequences = []
#         for obj in Appointment.objects.filter(
#                 registered_subject=self.registered_subject,
#                 visit_definition=self.appointment.visit_definition):
#             visit_code_sequences.append(obj.visit_code_sequence)
#         self.assertEquals(visit_code_sequences, ['0'])
#         form = AppointmentForm(
#             {'appt_datetime': self.appointment.appt_datetime,
#              'appt_status': IN_PROGRESS,
#              'appt_type': 'clinic',
#              'registered_subject': self.appointment.registered_subject.id,
#              'visit_definition': self.appointment.visit_definition.id,
#              'visit_code_sequence': '1'},
#             instance=self.appointment)
#         self.assertFalse(form.is_valid())
#         self.assertIn(
#             'Attempt to create or update appointment instance out of sequence. Got \'1000.1\'.',
#             form.errors.get('__all__'))
# 
#     def test_form(self):
#         """Asserts cannot create duplicate appointment"""
#         Appointment.objects.all().update(appt_status=NEW_APPT)
#         data = dict(
#             registered_subject=self.registered_subject.pk,
#             appt_datetime=timezone.now(),
#             appt_status=IN_PROGRESS,
#             visit_definition=self.visit_definition.pk,
#             visit_code_sequence='0',
#             appt_type='clinic'
#         )
#         form = AppointmentForm(data)
#         form.is_valid()
#         self.assertIn(
#             'Appointment with this Registered subject, Visit and Instance already exists.',
#             form.errors.get('__all__'))
# 
#     def test_form_save(self):
#         """Asserts can create a new appointment."""
#         Appointment.objects.all().delete()
#         data = dict(
#             registered_subject=self.registered_subject.pk,
#             appt_datetime=timezone.now(),
#             appt_status=IN_PROGRESS,
#             visit_definition=self.visit_definition.pk,
#             visit_code_sequence='0',
#             appt_type='clinic'
#         )
#         form = AppointmentForm(data)
#         self.assertTrue(form.is_valid())
#         with self.assertRaises(forms.ValidationError):
#             try:
#                 form.save()
#             except:
#                 pass
#             else:
#                 raise forms.ValidationError('ValidationError not raised')
# 
#     def test_form_save_creates_timepoint_status(self):
#         """Asserts can new appointment creates time_point_status."""
#         Appointment.objects.all().delete()
#         data = dict(
#             registered_subject=self.registered_subject.pk,
#             appt_datetime=timezone.now(),
#             appt_status=IN_PROGRESS,
#             visit_definition=self.visit_definition.pk,
#             visit_code_sequence='0',
#             appt_type='clinic'
#         )
#         form = AppointmentForm(data)
#         self.assertTrue(form.is_valid())
#         form.save()
#         appointment = Appointment.objects.get(
#             registered_subject=self.registered_subject.pk,
#             visit_definition=self.visit_definition.pk,
#             visit_code_sequence='0')
#         self.assertTrue(appointment.time_point_status)
#         with self.assertRaises(TimePointStatus.DoesNotExist):
#             try:
#                 TimePointStatus.objects.get(
#                     visit_code=appointment.visit_definition.code,
#                     subject_identifier=appointment.registered_subject.subject_identifier)
#             except:
#                 pass
#             else:
#                 raise TimePointStatus.DoesNotExist('TimePointStatus.DoesNotExist not raised')
# 
#     def test_form_save_does_not_create_timepoint_status(self):
#         """Asserts an existing appointment does not create a new time_point_status."""
#         Appointment.objects.all().update(appt_status=NEW_APPT)
#         self.assertEqual(Appointment.objects.filter(appt_status=IN_PROGRESS).count(), 0)
#         form = AppointmentForm(
#             {'appt_datetime': self.appointment.appt_datetime,
#              'appt_status': IN_PROGRESS,
#              'appt_type': 'clinic',
#              'registered_subject': self.appointment.registered_subject.id,
#              'visit_definition': self.appointment.visit_definition.id},
#             instance=self.appointment)
#         self.assertTrue(form.is_valid())
#         form.save()
#         appointment = Appointment.objects.get(
#             registered_subject=self.registered_subject.pk,
#             visit_definition=self.visit_definition.pk,
#             visit_code_sequence='0')
#         self.assertTrue(appointment.time_point_status)
#         with self.assertRaises(TimePointStatus.DoesNotExist):
#             try:
#                 TimePointStatus.objects.get(
#                     visit_code=appointment.visit_definition.code,
#                     subject_identifier=appointment.registered_subject.subject_identifier)
#             except:
#                 pass
#             else:
#                 raise TimePointStatus.DoesNotExist('TimePointStatus.DoesNotExist not raised')
# 
#     def test_form_save_bad_visit_code_sequence(self):
#         """Aseerts cannot create 1000.1 if 1000.0 does not exist."""
#         Appointment.objects.all().delete()
#         data = dict(
#             registered_subject=self.registered_subject.pk,
#             appt_datetime=timezone.now(),
#             appt_status=IN_PROGRESS,
#             visit_definition=self.visit_definition.pk,
#             visit_code_sequence='1',
#             appt_type='clinic')
#         form = AppointmentForm(data)
#         self.assertFalse(form.is_valid())
#         self.assertIn(
#             'Attempt to create or update appointment instance out of sequence. Got \'1000.1\'.',
#             form.errors.get('__all__'))
# 
#     def test_form_appt_status_complete(self):
#         """Asserts can be set to complete if visit form not keyed."""
#         Appointment.objects.all().delete()
#         data = dict(
#             appt_datetime=timezone.now(),
#             appt_status=COMPLETE_APPT,
#             appt_type='clinic',
#             registered_subject=self.registered_subject.pk,
#             visit_definition=self.visit_definition.pk,
#             visit_code_sequence='0',
#         )
#         form = AppointmentForm(data=data)
#         self.assertTrue(form.is_valid())
# 
#     def test_cannot_change_registered_subject_for_existing_appt(self):
#         """Asserts an existing appointment cannot change registered_subject."""
#         Appointment.objects.all().update(appt_status=NEW_APPT)
#         self.assertEqual(Appointment.objects.filter(appt_status=IN_PROGRESS).count(), 0)
#         form = AppointmentForm(
#             {'appt_datetime': self.appointment.appt_datetime,
#              'appt_status': IN_PROGRESS,
#              'appt_type': 'clinic',
#              'registered_subject': self.registered_subject2.id,
#              'visit_definition': self.appointment.visit_definition.id},
#             instance=self.appointment)
#         form.is_valid()
#         self.assertIn(
#             'Registered Subject cannot be changed for an existing appointment.',
#             form.errors.get('__all__'))
# 
#     def test_cannot_change_visit_definition_for_existing_appt(self):
#         """Asserts an existing appointment cannot change visit_definition."""
#         Appointment.objects.all().update(appt_status=NEW_APPT)
#         another_visit_definition = VisitDefinition.objects.get(code='2000')
#         self.assertEqual(Appointment.objects.filter(appt_status=IN_PROGRESS).count(), 0)
#         form = AppointmentForm(
#             {'appt_datetime': self.appointment.appt_datetime,
#              'appt_status': IN_PROGRESS,
#              'appt_type': 'clinic',
#              'registered_subject': self.registered_subject.id,
#              'visit_definition': another_visit_definition.id},
#             instance=self.appointment)
#         form.is_valid()
#         self.assertIn(
#             'Visit Definition cannot be changed for an existing appointment.',
#             form.errors.get('__all__'))
