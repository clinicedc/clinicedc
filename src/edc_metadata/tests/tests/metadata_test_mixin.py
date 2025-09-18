from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.models import SubjectConsentV1
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from django.test import TestCase
from django.utils import timezone

from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_facility.import_holidays import import_holidays
from edc_lab.models import Panel
from edc_metadata.models import CrfMetadata, RequisitionMetadata
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

test_datetime = datetime(2019, 6, 11, 8, 00, tzinfo=ZoneInfo("UTC"))


class TestMetadataMixin(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        traveller = time_machine.travel(test_datetime)
        traveller.start()
        self.panel_one = Panel.objects.create(name="one")
        self.panel_two = Panel.objects.create(name="two")

        for name in ["three", "four", "five", "six"]:
            Panel.objects.create(name=name)

        site_consents.registry = {}
        site_consents.register(consent_v1)

        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(get_visit_schedule(consent_v1))

        self.subject_identifier = "1111111"
        self.assertEqual(CrfMetadata.objects.all().count(), 0)
        self.assertEqual(RequisitionMetadata.objects.all().count(), 0)
        subject_consent = SubjectConsentV1.objects.create(
            subject_identifier=self.subject_identifier, consent_datetime=timezone.now()
        )
        _, self.schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_visit_schedule.onschedule"
        )
        self.schedule.put_on_schedule(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
            # consent_definition=subject_consent.consent_definition,
        )
        self.appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code=self.schedule.visits.first.code,
        )

        self.appointment_2000 = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code="2000",
        )
        traveller.stop()
