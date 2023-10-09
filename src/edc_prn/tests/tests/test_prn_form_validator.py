from django import forms
from django.test import TestCase, override_settings
from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_consent.modelform_mixins import RequiresConsentModelFormMixin
from edc_facility import import_holidays
from edc_form_validators import FormValidator, FormValidatorMixin
from edc_reference import site_reference_configs
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.tests.helper import Helper
from visit_schedule_app.consents import v1_consent
from visit_schedule_app.models import SubjectConsent, SubjectVisit

from ...modelform_mixins import PrnFormValidatorMixin
from ..models import Prn
from ..visit_schedule import visit_schedule


@override_settings(
    SUBJECT_CONSENT_MODEL="visit_schedule_app.subjectconsent",
    SUBJECT_SCREENING_MODEL="visit_schedule_app.subjectscreening",
)
class EdcCrfTestCase(TestCase):
    helper_cls = Helper

    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super().setUpClass()

    def setUp(self):
        self.subject_identifier = "12345"
        site_consents.registry = {}
        site_consents.register(v1_consent)
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier,
            subject_consent_model_cls=SubjectConsent,
            onschedule_model_name="visit_schedule_app.onschedule",
        )
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule)
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "edc_visit_tracking.subjectvisit"}
        )
        self.subject_consent = self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all()[0]
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
