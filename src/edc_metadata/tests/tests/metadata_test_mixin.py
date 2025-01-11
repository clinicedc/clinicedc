from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.test import TestCase
from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_consent.consent_definition import ConsentDefinition
from edc_constants.constants import FEMALE, MALE
from edc_facility import import_holidays
from edc_lab.models import Panel
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ...models import CrfMetadata, RequisitionMetadata
from ..models import SubjectConsentV1
from ..visit_schedule import get_visit_schedule

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

        consent_v1 = ConsentDefinition(
            "edc_metadata.subjectconsentv1",
            version="1",
            start=get_utcnow(),
            end=get_utcnow() + relativedelta(years=3),
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

        self.appointment_2000 = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code="2000",
        )
        traveller.stop()
