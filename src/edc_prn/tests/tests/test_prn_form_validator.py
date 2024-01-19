from django import forms
from django.test import TestCase, override_settings
from edc_appointment.models import Appointment
from edc_consent.modelform_mixins import RequiresConsentModelFormMixin
from edc_consent.site_consents import site_consents
from edc_facility import import_holidays
from edc_form_validators import FormValidator, FormValidatorMixin
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit
from visit_schedule_app.consents import v1_consent

from ...modelform_mixins import PrnFormValidatorMixin
from ..helper import Helper
from ..models import Prn
from ..visit_schedule import visit_schedule


@override_settings(SITE_ID=10)
class TestPrn(TestCase):
    helper_cls = Helper

    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super().setUpClass()

    def setUp(self):
        self.subject_identifier = "12345"
        site_consents.registry = {}
        site_consents.register(v1_consent)
        self.helper = self.helper_cls(subject_identifier=self.subject_identifier)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule)
        schedule = visit_schedule.schedules.get("schedule")
        self.subject_consent = self.helper.consent_and_put_on_schedule(
            visit_schedule_name=visit_schedule.name, schedule_name=schedule.name
        )
        appointment = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[0]
        self.subject_visit = SubjectVisit.objects.create(
            appointment=appointment, report_datetime=get_utcnow(), reason=SCHEDULED
        )
        self.report_datetime = self.subject_visit.report_datetime

    def test_form_validator_with_prn(self):
        class MyFormValidator(PrnFormValidatorMixin, FormValidator):
            report_datetime_field_attr = "report_datetime"

            def clean(self) -> None:
                """test all methods"""
                _ = self.subject_consent
                _ = self.subject_identifier
                _ = self.report_datetime

        class MyForm(
            RequiresConsentModelFormMixin,
            FormValidatorMixin,
            forms.ModelForm,
        ):
            form_validator_cls = MyFormValidator

            def validate_against_consent(self):
                pass

            class Meta:
                model = Prn
                fields = "__all__"

        data = dict(
            subject_identifier=self.subject_consent.subject_identifier,
            report_datetime=self.report_datetime,
        )
        form = MyForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)
