from datetime import date
from dateutil.relativedelta import relativedelta

from django.apps import apps as django_apps
from django import forms
from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured

from django.test.testcases import TestCase

from edc_constants.constants import ON_STUDY, ALIVE, YES
from edc_visit_tracking.form_mixins import VisitFormMixin
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from edc_example.models import SubjectVisit, Appointment, CrfOne, SubjectConsent, Enrollment, CrfOneInline, OtherModel,\
    BadCrfOneInline
from edc_example.factories import SubjectConsentFactory, SubjectVisitFactory
from edc_consent.form_mixins import RequiresConsentFormMixin

# from .base_test_case import BaseTestCase


class SubjectVisitForm(VisitFormMixin, RequiresConsentFormMixin, forms.ModelForm):

    class Meta:
        model = SubjectVisit
        fields = '__all__'


class TestVisitMixin(TestCase):

    def test_crf_visit_model_attrs(self):
        """Assert models using the CrfModelMixin can determine which
        attribute points to the visit model foreignkey."""
        self.assertEqual(CrfOne().visit_model_attr(), 'subject_visit')
        self.assertEqual(CrfOne.objects.all().count(), 0)

    def test_crf_visit_model(self):
        """Assert models using the CrfModelMixin can determine which
        visit model is in use for the app_label"""
        self.assertEqual(CrfOne().visit_model(), SubjectVisit)
        self.assertEqual(CrfOne.objects.all().count(), 0)

    def test_crf_inline_model_attrs(self):
        """Assert inline model can find visit instance from parent."""
        subject_consent = SubjectConsentFactory()
        Enrollment.objects.create(subject_identifier=subject_consent.subject_identifier)
        appointment = Appointment.objects.all()[0]
        subject_visit = SubjectVisitFactory(appointment=appointment)
        crf_one = CrfOne.objects.create(subject_visit=subject_visit)
        other_model = OtherModel.objects.create()
        crf_one_inline = CrfOneInline.objects.create(crf_one=crf_one, other_model=other_model)
        self.assertEqual(crf_one_inline.visit.pk, subject_visit.pk)

    def test_crf_inline_model_parent_model(self):
        """Assert inline model cannot find parent, raises exception."""
        subject_consent = SubjectConsentFactory()
        Enrollment.objects.create(subject_identifier=subject_consent.subject_identifier)
        appointment = Appointment.objects.all()[0]
        subject_visit = SubjectVisitFactory(appointment=appointment)
        crf_one = CrfOne.objects.create(subject_visit=subject_visit)
        other_model = OtherModel.objects.create()
        self.assertRaises(ImproperlyConfigured, BadCrfOneInline.objects.create, crf_one=crf_one, other_model=other_model)


class TestVisit(TestCase):

    def setUp(self):
        app_config = django_apps.get_app_config('edc_registration')
        RegisteredSubject = app_config.model
        subject_identifier = '123456789-0'
        # consent
        self.subject_consent = SubjectConsentFactory(
            subject_identifier=subject_identifier,
            consent_datetime=timezone.now(),
            identity='111211111',
            confirm_identity='111211111',
            is_literate=YES)
        # verify registered_subject created
        self.registered_subject = RegisteredSubject.objects.get(
            subject_identifier='123456789-0')
        # enroll consented subject
        enrollment = Enrollment.objects.create(subject_identifier=self.subject_consent.subject_identifier)
        visit_schedule = site_visit_schedules.get_visit_schedule(enrollment._meta.visit_schedule_name)
        schedule = visit_schedule.get_schedule(enrollment._meta.label_lower)
        # verify appointments created as per edc_example visit_schedule "subject_visit_schedule"
        self.assertEqual(Appointment.objects.all().count(), 4)
        # get appointment for first visit
        visit = schedule.get_first_visit()
        appointment = Appointment.objects.get(
            subject_identifier=subject_identifier,
            visit_code=visit.code,
            visit_instance='0')
        self.data = {
            'appointment': appointment.pk,
            'report_datetime': timezone.now(),
            'study_status': ON_STUDY,
            'survival_status': ALIVE,
            'require_crfs': YES,
            'info_source': 'clinic',
            'last_alive_date': date.today(),
            'reason': SCHEDULED,
        }

    def test_crf_inline_model_attrs(self):
        """Assert inline model can find visit instance from parent."""
        form = SubjectVisitForm(self.data)
        self.assertTrue(form.is_valid())
        subject_visit = form.save()
        crf_one = CrfOne.objects.create(subject_visit=subject_visit)
        other_model = OtherModel.objects.create()
        crf_one_inline = CrfOneInline.objects.create(
            crf_one=crf_one,
            other_model=other_model)
        self.assertIsInstance(crf_one_inline.visit, SubjectVisit)

    def test_form(self):
        form = SubjectVisitForm(self.data)
        self.assertTrue(form.is_valid())

    def test_form_before_consent(self):
        self.data.update({'report_datetime': timezone.now() - relativedelta(years=1)})
        form = SubjectVisitForm(self.data)
        self.assertFalse(form.is_valid())
        self.assertIn('Report datetime cannot be before consent datetime', form.errors.get('__all__') or [])

    def test_form_before_dob(self):
        self.subject_consent.consent_datetime = timezone.now() - relativedelta(days=30)
        self.subject_consent.dob = timezone.now().date() - relativedelta(days=10)
        self.subject_consent.save()
        self.data.update({'report_datetime': timezone.now() - relativedelta(days=15)})
        form = SubjectVisitForm(self.data)
        self.assertFalse(form.is_valid())
        self.assertIn('Report datetime cannot be before DOB', form.errors.get('__all__') or [])
