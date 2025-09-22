from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from django.test import TestCase

from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_constants.constants import MALE
from edc_facility.import_holidays import import_holidays
from edc_lab.models import Panel
from edc_metadata.models import CrfMetadata, RequisitionMetadata
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

utc_tz = ZoneInfo("UTC")


@time_machine.travel(datetime(2019, 8, 11, 8, 00, tzinfo=utc_tz))
class TestMetadataMixin(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        self.panel_one = Panel.objects.create(name="one")
        self.panel_two = Panel.objects.create(name="two")

        for name in ["three", "four", "five", "six"]:
            Panel.objects.create(name=name)

        self.assertEqual(CrfMetadata.objects.all().count(), 0)
        self.assertEqual(RequisitionMetadata.objects.all().count(), 0)

        helper = Helper()
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(get_visit_schedule(consent_v1))
        # note crfs in visit schedule are all set to REQUIRED by default.
        self.visit_schedule, self.schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_visit_schedule.onschedule"
        )
        self.subject_visit = helper.enroll_to_baseline(
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            gender=MALE,
        )
        self.subject_identifier = self.subject_visit.subject_identifier

        self.appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code=self.schedule.visits.first.code,
        )

        self.appointment_2000 = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code="2000",
        )
