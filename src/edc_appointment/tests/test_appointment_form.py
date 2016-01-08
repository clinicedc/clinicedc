from datetime import date
from dateutil.relativedelta import relativedelta

from django.db import models
from django.utils import timezone

from edc_appointment.forms.appointment_form import AppointmentForm
from edc_appointment.models import AppointmentMixin, Appointment
from edc_appointment.tests.test_models import TestCrfModel1, TestCrfModel2, TestCrfModel3, TestRequisitionModel
from edc_constants.constants import (
    NEW_APPT, COMPLETE_APPT, MALE, YES, SCHEDULED, IN_PROGRESS)
from edc_registration.models import RegisteredSubject
from edc_testing.models.test_panel import TestPanel
from edc_testing.models.test_aliquot_type import TestAliquotType
from edc_testing.tests.factories import TestConsentWithMixinFactory
from edc_testing.models.test_visit import TestVisit
from edc_visit_schedule.models.visit_definition import VisitDefinition


from .base_test_case import BaseTestCase


class TestRegistrationModel(AppointmentMixin, models.Model):

    registered_subject = models.ForeignKey(RegisteredSubject)

    report_datetime = models.DateTimeField(default=timezone.now())

    class Meta:
        app_label = 'edc_appointment'


class TestAppointmentForm(BaseTestCase):

    def setUp(self):
        super(TestAppointmentForm, self).setUp()
        TestConsentWithMixinFactory(
            registered_subject=self.registered_subject,
            consent_datetime=timezone.now(),
            gender=MALE,
            is_literate=YES,
            dob=date.today() - relativedelta(years=35),
            identity='111111111',
            confirm_identity='111111111',
            subject_identifier='999-100000-1',
            study_site=self.study_site)
        visit_definition = VisitDefinition.objects.get(code='1000')
        self.appointment = Appointment.objects.get(
            registered_subject=self.registered_subject,
            visit_definition=visit_definition)
        self.test_visit = TestVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED, report_datetime=timezone.now())
        self.panel = TestPanel.objects.first()
        self.aliquot_type = TestAliquotType.objects.first()

    def test_form_appt_status_complete(self):
        """Asserts appointment cannot be complete if unkeyed CRFs exists."""
        form = AppointmentForm(
            {'appt_status': COMPLETE_APPT,
             'registered_subject': self.appointment.registered_subject.id},
            instance=self.appointment)
        self.assertFalse(form.is_valid())
        self.assertIn(
            'Appointment is not \'complete\'. Some CRFs are still required.',
            form.errors.get('__all__'))

    def test_form_appt_status_complete2(self):
        """Asserts appointment cannot be complete if unkeyed requisitions exists."""
        TestCrfModel1.objects.create(test_visit=self.test_visit)
        TestCrfModel2.objects.create(test_visit=self.test_visit)
        TestCrfModel3.objects.create(test_visit=self.test_visit)
        form = AppointmentForm(
            {'appt_status': COMPLETE_APPT,
             'registered_subject': self.appointment.registered_subject.id},
            instance=self.appointment)
        self.assertFalse(form.is_valid())
        self.assertIn(
            'Appointment is not \'complete\'. Some Requisitions are still required.',
            form.errors.get('__all__'))

    def test_form_appt_status_new_keyed(self):
        """Asserts that an appointment cannot new if keyed CRFs meta data exists."""
        TestCrfModel1.objects.create(test_visit=self.test_visit)
        form = AppointmentForm(
            {'appt_status': NEW_APPT,
             'registered_subject': self.appointment.registered_subject.id,
             'appt_datetime': self.appointment.appt_datetime,
             'appt_type': 'clinic',
             'visit_definition': self.appointment.visit_definition.id},
            instance=self.appointment)
        self.assertFalse(form.is_valid())
        self.assertIn(
            'Appointment is not \'new\'. Some CRFs have been completed.',
            form.errors.get('__all__') or [])

    def test_form_appt_status_new_keyed2(self):
        """Asserts that an appointment cannot new if keyed Requisition meta data exists."""
        TestRequisitionModel.objects.create(
            test_visit=self.test_visit,
            panel=self.panel,
            aliquot_type=self.aliquot_type)
        form = AppointmentForm(
            {'appt_status': NEW_APPT,
             'registered_subject': self.appointment.registered_subject.id,
             'appt_datetime': self.appointment.appt_datetime,
             'appt_type': 'clinic',
             'visit_definition': self.appointment.visit_definition.id},
            instance=self.appointment)
        self.assertFalse(form.is_valid())
        self.assertIn(
            'Appointment is not \'new\'. Some Requisitions have been completed.',
            form.errors.get('__all__') or [])

    def test_form_appt_status_in_progress_not_allowed(self):
        """Asserts appointment cannot be in progress while another is already in progress."""
        Appointment.objects.all().update(appt_status=NEW_APPT)
        self.assertEqual(Appointment.objects.filter(appt_status=IN_PROGRESS).count(), 0)
        self.appointment.appt_status = IN_PROGRESS
        self.appointment.save()
        visit_definition = VisitDefinition.objects.get(code='2000')
        appointment = Appointment.objects.get(
            registered_subject=self.registered_subject,
            visit_definition=visit_definition)
        form = AppointmentForm(
            {'appt_status': IN_PROGRESS,
             'registered_subject': appointment.registered_subject.id,
             'appt_datetime': appointment.appt_datetime,
             'appt_type': 'clinic',
             'visit_definition': appointment.visit_definition.id},
            instance=appointment)
        self.assertFalse(form.is_valid())
        self.assertIn(
            'Another appointment is currently \'in progress\'. Only one appointment '
            'may be in progress at a time. Please resolve before continuing.',
            form.errors.get('__all__') or [])

    def test_form_appt_status_in_progress_allowed(self):
        """Asserts appointment can be in progress if no others are."""
        Appointment.objects.all().update(appt_status=NEW_APPT)
        self.assertEqual(Appointment.objects.filter(appt_status=IN_PROGRESS).count(), 0)
        form = AppointmentForm(
            {'appt_status': IN_PROGRESS,
             'registered_subject': self.appointment.registered_subject.id,
             'appt_datetime': self.appointment.appt_datetime,
             'appt_type': 'clinic',
             'visit_definition': self.appointment.visit_definition.id},
            instance=self.appointment)
        self.assertTrue(form.is_valid())

    def test_form_appt_out_of_sequence(self):
        """Asserts appointment visit instance must increment by 1."""
        visit_instances = []
        for obj in Appointment.objects.filter(
                registered_subject=self.registered_subject,
                visit_definition=self.appointment.visit_definition):
            visit_instances.append(obj.visit_instance)
        self.assertEquals(visit_instances, ['0'])
        form = AppointmentForm(
            {'appt_datetime': self.appointment.appt_datetime,
             'appt_status': IN_PROGRESS,
             'appt_type': 'clinic',
             'registered_subject': self.appointment.registered_subject.id,
             'visit_definition': self.appointment.visit_definition.id,
             'visit_instance': '5'},
            instance=self.appointment)
        self.assertFalse(form.is_valid())
        self.assertIn(
            'Attempt to create or update appointment instance out of sequence. Got \'1000.5\'.',
            form.errors.get('__all__'))
