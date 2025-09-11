from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.utils import get_user_for_tests
from clinicedc_tests.visit_schedules.visit_schedule_metadata.visit_schedule import (
    get_visit_schedule,
)
from django.test import TestCase
from django.test.client import RequestFactory

from edc_consent import site_consents
from edc_facility.import_holidays import import_holidays
from edc_form_validators.form_validator import FormValidator
from edc_lab.models import Panel
from edc_metadata.metadata_helper import MetadataHelperMixin
from edc_metadata.metadata_rules import site_metadata_rules
from edc_metadata.models import CrfMetadata, RequisitionMetadata
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from .test_view_mixin import MyView


class MyForm(MetadataHelperMixin, FormValidator):
    pass


utc_tz = ZoneInfo("UTC")


@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=utc_tz))
class TestForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        helper = Helper()
        site_metadata_rules.registry = {}

        self.user = get_user_for_tests(username="erik")

        for name in ["one", "two", "three", "four", "five", "six", "seven", "eight"]:
            Panel.objects.create(name=name)

        self.assertEqual(CrfMetadata.objects.all().count(), 0)
        self.assertEqual(RequisitionMetadata.objects.all().count(), 0)

        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(get_visit_schedule(consent_v1))

        self.subject_visit = helper.enroll_to_baseline(consent_definition=consent_v1)
        self.subject_identifier = self.subject_visit.subject_identifier
        self.appointment = self.subject_visit.appointment

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
