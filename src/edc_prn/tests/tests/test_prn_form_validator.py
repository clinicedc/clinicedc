from django import forms
from django.contrib.sites.models import Site
from django.test import TestCase
from edc_appointment.models import Appointment
from edc_consent.modelform_mixins import RequiresConsentModelFormMixin
from edc_consent.site_consents import site_consents
from edc_facility import import_holidays
from edc_form_validators import FormValidator, FormValidatorMixin
from edc_sites.modelform_mixins import SiteModelFormMixin
from edc_sites.utils import add_or_update_django_sites
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit

from edc_prn.modelform_mixins import PrnFormValidatorMixin
from prn_app.consents import consent_v1
from prn_app.models import Prn
from prn_app.visit_schedule import visit_schedule

from ..helper import Helper


class TestPrn(TestCase):
    helper_cls = Helper

    @classmethod
    def setUpTestData(cls):
        import_holidays()
        add_or_update_django_sites()

    def setUp(self):
        self.subject_identifier = "12345"
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule)
        schedule = visit_schedule.schedules.get("schedule")
        self.helper = self.helper_cls(subject_identifier=self.subject_identifier)
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
                # _ = self.subject_consent
                _ = self.subject_identifier
                _ = self.report_datetime

        class MyForm(
            SiteModelFormMixin,
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
            site=Site.objects.get_current(),
        )
        form = MyForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)
