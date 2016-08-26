from datetime import date
from dateutil.relativedelta import relativedelta

from django import forms
from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured

from django.test.testcases import TestCase

from edc_constants.constants import ON_STUDY, ALIVE, YES
from edc_visit_tracking.form_mixins import VisitFormMixin
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from edc_example.models import SubjectVisit, Appointment, CrfOne, SubjectConsent, Enrollment  # OffStudyReport, DeathReport, CrfOneInline,\
from django_extensions.management.commands.update_permissions import django_apps

# from .base_test_case import BaseTestCase


class TestVisitForm(VisitFormMixin, forms.ModelForm):

    class Meta:
        model = SubjectVisit
        fields = '__all__'


class TestVisitA(TestCase):

    def test_crf_visit_model_attrs(self):
        """Assert models using the CrfModelMixin can determine which
        attribute points to the visit model foreignkey."""
        self.assertEqual(CrfOne().visit_model_attr, 'subject_visit')
        self.assertEqual(CrfOne.objects.all().count(), 0)

    def test_crf_visit_model(self):
        """Assert models using the CrfModelMixin can determine which
        visit model is in use for the app_label"""
        self.assertEqual(CrfOne().visit_model, SubjectVisit)
        self.assertEqual(CrfOne.objects.all().count(), 0)

    def test_crf_inline_model_attrs(self):
        """Assert inline model can find visit instance from parent."""
        appointment = Appointment()
        test_crf_model = CrfOne.objects.create(subject_visit=subject_visit)
        test_crf_inline_model = CrfOneInline.objects.create(
            test_crf_model=test_crf_model)
        self.assertIsInstance(test_crf_inline_model.get_visit(), SubjectVisit)
        self.assertRaises(AttributeError, test_crf_inline_model.visit_model)
        self.assertRaises(AttributeError, test_crf_inline_model.visit_model_attr)


class TestVisit(TestCase):

    def setUp(self):
        app_config = django_apps.get_app_config('edc_registration')
        RegisteredSubject = app_config.model
        subject_identifier = '123456789-0'
        # consent
        subject_consent = SubjectConsent.objects.create(
            subject_identifier=subject_identifier,
            consent_datetime=timezone.now(),
            identity='111211111',
            confirm_identity='111211111',
            is_literate=YES)
        # verify registered_subject created
        self.registered_subject = RegisteredSubject.objects.get(
            subject_identifier='123456789-0')
        # enroll consented subject
        enrollment = Enrollment.objects.create(subject_identifier=subject_consent.subject_identifier)
        visit_schedule = site_visit_schedules.get_visit_schedule(enrollment.visit_schedule_name)
        schedule = visit_schedule.get_schedule(enrollment.label_lower)
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
        form = TestVisitForm(data=self.data)
        self.assertTrue(form.is_valid())
        subject_visit = form.save()
        test_crf_model = CrfOne.objects.create(subject_visit=subject_visit)
        test_crf_inline_model = CrfOneInline.objects.create(
            test_crf_model=test_crf_model)
        self.assertIsInstance(test_crf_inline_model.get_visit(), SubjectVisit)
        self.assertRaises(AttributeError, test_crf_inline_model.visit_model)
        self.assertRaises(AttributeError, test_crf_inline_model.visit_model_attr)

    def test_crf_proxy_model_attrs(self):
        """Assert proxy model can find visit attrs from parent."""
        form = TestVisitForm(data=self.data)
        self.assertTrue(form.is_valid())
        test_visit = form.save()
        test_crf_proxy_model = TestCrfProxyModel.objects.create(test_visit=test_visit)
        self.assertIsInstance(test_crf_proxy_model.get_visit(), SubjectVisit)
        self.assertEquals(test_crf_proxy_model.visit_model, SubjectVisit)
        self.assertEquals(test_crf_proxy_model.visit_model_attr, 'test_visit')

    def test_raise_on_crf_inline_ambiguous_fks(self):
        """Assert raises exception if _meta.crf_inline_parent_model not set and model
        has more than one FK."""
        self.assertRaises(ImproperlyConfigured, TestCrfInlineModel2)

    def test_not_raised_on_crf_inline_explicit_parent_model(self):
        """Assert does not raise exception if _meta.crf_inline_parent_model is explicitly set on a model
        that has more than one FK."""
        with self.assertRaises(ImproperlyConfigured):
            try:
                obj = TestCrfInlineModel3()
            except ImproperlyConfigured:
                pass
            else:
                raise ImproperlyConfigured
        self.assertEqual(obj._meta.crf_inline_parent_model, 'another_key')

    def test_form(self):
        form = TestVisitForm(data=self.data)
        self.assertTrue(form.is_valid())

    def test_form_before_consent(self):
        self.data.update({'report_datetime': timezone.now() - relativedelta(years=1)})
        form = TestVisitForm(data=self.data)
        self.assertFalse(form.is_valid())
        self.assertIn('Report datetime cannot be before consent datetime', form.errors.get('__all__') or [])

    def test_form_before_dob(self):
        self.data.update({'report_datetime': timezone.now() - relativedelta(years=25)})
        form = TestVisitForm(data=self.data)
        self.assertFalse(form.is_valid())
        self.assertIn('Report datetime cannot be before consent datetime', form.errors.get('__all__') or [])
