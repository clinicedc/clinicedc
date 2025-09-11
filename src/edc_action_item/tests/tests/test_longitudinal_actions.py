from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.action_items import (
    CrfLongitudinalOneAction,
    CrfLongitudinalTwoAction,
)
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import CrfLongitudinalOne
from clinicedc_tests.visit_schedules.visit_schedule_action_item import (
    get_visit_schedule,
)
from django.apps import apps as django_apps
from django.test import TestCase, override_settings, tag

from edc_action_item.models import ActionItem
from edc_action_item.site_action_items import site_action_items
from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from ..test_case_mixin import TestCaseMixin

utc_tz = ZoneInfo("UTC")


@tag("action_item")
@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=utc_tz))
@override_settings(SITE_ID=30)
class TestLongitudinal(TestCaseMixin, TestCase):

    def setUp(self):
        helper = Helper()
        site_action_items.registry = {}
        site_action_items.register(CrfLongitudinalOneAction)
        site_action_items.register(CrfLongitudinalTwoAction)
        site_consents.registry = {}
        site_consents.register(consent_v1)

        visit_schedule = get_visit_schedule(consent_v1)
        schedule = visit_schedule.schedules.get("schedule_action_item")
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)

        subject_consent = helper.consent_and_put_on_schedule(
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
            consent_definition=consent_v1,
        )
        self.subject_identifier = subject_consent.subject_identifier

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
