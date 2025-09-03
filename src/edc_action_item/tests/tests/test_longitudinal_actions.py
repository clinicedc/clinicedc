from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from django.apps import apps as django_apps
from django.test import tag, TestCase

from edc_action_item.models import ActionItem
from edc_action_item.site_action_items import site_action_items
from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_facility.import_holidays import import_holidays
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from tests.action_items import CrfLongitudinalOneAction, CrfLongitudinalTwoAction
from tests.consents import consent_v1
from tests.helper import Helper
from tests.models import CrfLongitudinalOne
from tests.visit_schedules.visit_schedule import get_visit_schedule
from ..test_case_mixin import TestCaseMixin

utc_tz = ZoneInfo("UTC")


@tag("action_item")
@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=utc_tz))
class TestLongitudinal(TestCaseMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super().setUpClass()

    def setUp(self):
        helper = Helper()
        site_action_items.registry = {}
        site_action_items.register(CrfLongitudinalOneAction)
        site_action_items.register(CrfLongitudinalTwoAction)
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(get_visit_schedule(consent_v1))

        self.subject_identifier = helper.consent_and_put_on_schedule(
            consent_definition=consent_v1
        )

    def test_(self):
        appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code="1000",
        )
        traveller = time_machine.travel(appointment.appt_datetime)
        traveller.start()
        subject_visit = django_apps.get_model(
            "edc_visit_tracking.subjectvisit"
        ).objects.create(
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
            reason=SCHEDULED,
        )
        crf_one_a = CrfLongitudinalOne.objects.create(subject_visit=subject_visit)
        ActionItem.objects.get(action_identifier=crf_one_a.action_identifier)
        appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code="2000",
        )
        traveller.stop()
        traveller = time_machine.travel(appointment.appt_datetime)
        traveller.start()
        subject_visit = django_apps.get_model(
            "edc_visit_tracking.subjectvisit"
        ).objects.create(
            appointment=appointment,
            reason=SCHEDULED,
        )

        crf_one_b = CrfLongitudinalOne.objects.create(subject_visit=subject_visit)
        ActionItem.objects.get(action_identifier=crf_one_b.action_identifier)
        self.assertNotEqual(crf_one_a.action_identifier, crf_one_b.action_identifier)
        traveller.stop()
