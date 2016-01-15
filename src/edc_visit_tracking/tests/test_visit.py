from datetime import date

from django import forms

from django.utils import timezone

from edc_testing.models import TestVisit2
from edc_appointment.models.appointment import Appointment
from edc_constants.constants import SCHEDULED, ON_STUDY, ALIVE, YES
from edc_visit_schedule.models.visit_definition import VisitDefinition
from edc_visit_tracking.models import PreviousVisitError
from edc_visit_tracking.forms import VisitFormMixin

from .base_test_case import TestVisitModel, BaseTestCase
from edc_testing.models.test_consent import TestConsentWithMixin
from dateutil.relativedelta import relativedelta


class TesVisitForm(VisitFormMixin, forms.ModelForm):

    class Meta:
        model = TestVisitModel


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
