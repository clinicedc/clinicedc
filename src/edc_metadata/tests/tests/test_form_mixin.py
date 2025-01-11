from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.test.client import RequestFactory
from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_consent.consent_definition import ConsentDefinition
from edc_constants.constants import FEMALE, MALE
from edc_facility import import_holidays
from edc_form_validators.form_validator import FormValidator
from edc_lab.models import Panel
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from edc_metadata.metadata_helper import MetadataHelperMixin
from edc_metadata.metadata_rules import site_metadata_rules
from edc_metadata.models import CrfMetadata, RequisitionMetadata

from ..models import SubjectConsentV1, SubjectVisit
from ..visit_schedule import get_visit_schedule
from .test_view_mixin import MyView

test_datetime = datetime(2019, 6, 11, 8, 00, tzinfo=ZoneInfo("UTC"))


class MyForm(MetadataHelperMixin, FormValidator):
    pass


@override_settings(
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=test_datetime - relativedelta(years=3),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=test_datetime + relativedelta(years=3),
)
class TestForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        site_metadata_rules.registry = {}

        self.user = User.objects.create(username="erik")

        for name in ["one", "two", "three", "four", "five", "six", "seven", "eight"]:
            Panel.objects.create(name=name)

        consent_v1 = ConsentDefinition(
            "edc_metadata.subjectconsentv1",
            version="1",
            start=test_datetime,
            end=test_datetime + relativedelta(years=3),
            age_min=18,
            age_is_adult=18,
            age_max=64,
            gender=[MALE, FEMALE],
        )
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(get_visit_schedule(consent_v1))
        self.subject_identifier = "1111111"
        self.assertEqual(CrfMetadata.objects.all().count(), 0)
        self.assertEqual(RequisitionMetadata.objects.all().count(), 0)
        traveller = time_machine.travel(test_datetime)
        traveller.start()
        subject_consent = SubjectConsentV1.objects.create(
            subject_identifier=self.subject_identifier, consent_datetime=get_utcnow()
        )
        _, self.schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_metadata.onschedule"
        )
        self.schedule.put_on_schedule(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )
        self.appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code=self.schedule.visits.first.code,
        )
        self.subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment,
            subject_identifier=self.subject_identifier,
            report_datetime=self.appointment.appt_datetime,
            visit_code=self.appointment.visit_code,
            visit_code_sequence=self.appointment.visit_code_sequence,
            visit_schedule_name=self.appointment.visit_schedule_name,
            schedule_name=self.appointment.schedule_name,
            reason=SCHEDULED,
        )
        traveller.stop()

    @time_machine.travel(test_datetime)
    def test_ok(self):
        request = RequestFactory().get("/?f=f&e=e&o=o&q=q")
        request.user = self.user
        view = MyView(request=request, appointment=self.appointment)
        self.assertEqual("1000", self.appointment.visit_code)
        view.subject_identifier = self.subject_identifier
        view.kwargs = {}
        context_data = view.get_context_data()
        self.assertEqual(len(context_data.get("crfs")), 5)
        form = MyForm(cleaned_data={}, instance=view.appointment)
        self.assertTrue(form.crf_metadata_exists)
        self.assertTrue(form.crf_metadata_required_exists)
        self.assertTrue(form.requisition_metadata_exists)
        self.assertTrue(form.requisition_metadata_required_exists)
        form.validate()
