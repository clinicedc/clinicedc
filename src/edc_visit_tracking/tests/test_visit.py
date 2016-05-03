from datetime import date
from dateutil.relativedelta import relativedelta

from django import forms
from django.utils import timezone

from django.test.testcases import TestCase
from edc_appointment.models.appointment import Appointment
from edc_constants.constants import SCHEDULED, ON_STUDY, ALIVE, YES
from edc_testing.models import TestDeathReport, TestOffStudy
from edc_visit_schedule.models import VisitDefinition
from edc_visit_tracking.forms import VisitFormMixin

from .test_models import TestVisitModel, TestCrfModel
from .base_test_case import BaseTestCase
from edc_visit_tracking.tests.test_models import TestCrfInlineModel, TestCrfProxyModel, TestCrfInlineModel2,\
    TestCrfInlineModel3
from django.core.exceptions import ImproperlyConfigured


class TesVisitForm(VisitFormMixin, forms.ModelForm):

    class Meta:
        model = TestVisitModel
        fields = '__all__'

class TestVisitA(TestCase):

    def test_off_study_model_attr(self):
        self.assertEqual(TestVisitModel.off_study_model, TestOffStudy)
        self.assertEqual(TestVisitModel().off_study_model, TestOffStudy)
        self.assertEqual(TestVisitModel.objects.all().count(), 0)

    def test_death_report_model_attr(self):
        self.assertEqual(TestVisitModel.death_report_model, TestDeathReport)
        self.assertEqual(TestVisitModel().death_report_model, TestDeathReport)
        self.assertEqual(TestVisitModel.objects.all().count(), 0)

    def test_crf_model_attrs(self):
        self.assertEqual(TestCrfModel.visit_model, TestVisitModel)
        self.assertEqual(TestCrfModel().visit_model, TestVisitModel)
        self.assertEqual(TestCrfModel.objects.all().count(), 0)


class TestVisit(BaseTestCase):

    def setUp(self):
        super(TestVisit, self).setUp()
        visit_definition = VisitDefinition.objects.get(code='1000')
        appointment = Appointment.objects.get(
            registered_subject=self.registered_subject,
            visit_definition=visit_definition,
            visit_instance='0')
        TestVisitModel.consent_model.objects.get(
            registered_subject=appointment.registered_subject)
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
        form = TesVisitForm(data=self.data)
        self.assertTrue(form.is_valid())
        test_visit = form.save()
        test_crf_model = TestCrfModel.objects.create(test_visit=test_visit)
        test_crf_inline_model = TestCrfInlineModel.objects.create(
            test_crf_model=test_crf_model)
        self.assertIsInstance(test_crf_inline_model.get_visit(), TestVisitModel)
        self.assertRaises(AttributeError, test_crf_inline_model.visit_model)
        self.assertRaises(AttributeError, test_crf_inline_model.visit_model_attr)

    def test_crf_proxy_model_attrs(self):
        """Assert proxy model can find visit attrs from parent."""
        form = TesVisitForm(data=self.data)
        self.assertTrue(form.is_valid())
        test_visit = form.save()
        test_crf_proxy_model = TestCrfProxyModel.objects.create(test_visit=test_visit)
        self.assertIsInstance(test_crf_proxy_model.get_visit(), TestVisitModel)
        self.assertEquals(test_crf_proxy_model.visit_model, TestVisitModel)
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

    def test_model_attr(self):
        self.assertEqual(TestVisitModel.off_study_model, TestOffStudy)

    def test_form(self):
        form = TesVisitForm(data=self.data)
        self.assertTrue(form.is_valid())

    def test_form_before_consent(self):
        self.data.update({'report_datetime': timezone.now() - relativedelta(years=1)})
        form = TesVisitForm(data=self.data)
        self.assertFalse(form.is_valid())
        self.assertIn('Report datetime cannot be before consent datetime', form.errors.get('__all__') or [])

    def test_form_before_dob(self):
        self.data.update({'report_datetime': timezone.now() - relativedelta(years=25)})
        form = TesVisitForm(data=self.data)
        self.assertFalse(form.is_valid())
        self.assertIn('Report datetime cannot be before consent datetime', form.errors.get('__all__') or [])
