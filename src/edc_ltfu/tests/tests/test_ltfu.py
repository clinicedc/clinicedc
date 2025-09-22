from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.sites import all_sites
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, override_settings, tag
from django.utils import timezone

from edc_action_item.models import ActionItem
from edc_action_item.site_action_items import site_action_items
from edc_adverse_event.constants import DEATH_REPORT_ACTION
from edc_consent.site_consents import site_consents
from edc_constants.constants import CLOSED, YES
from edc_facility.import_holidays import import_holidays
from edc_ltfu.action_items import LtfuAction
from edc_ltfu.constants import LTFU_ACTION
from edc_ltfu.models import Ltfu
from edc_ltfu.utils import get_ltfu_model_cls, get_ltfu_model_name
from edc_offstudy.action_items import EndOfStudyAction as BaseEndOfStudyAction
from edc_sites.site import sites
from edc_sites.utils import add_or_update_django_sites
from edc_unblinding.constants import UNBLINDING_REVIEW_ACTION
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

utc_tz = ZoneInfo("UTC")


@tag("ltfu")
@override_settings(SITE_ID=10, EDC_SITES_REGISTER_DEFAULT=True)
@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=utc_tz))
class TestLtfu(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        sites._registry = {}
        sites.loaded = False
        sites.register(*all_sites)
        add_or_update_django_sites()

    def setUp(self):
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        visit_schedule = get_visit_schedule(consent_v1)
        site_visit_schedules.register(visit_schedule)

        helper = Helper()
        self.subject_identifiers = []
        for _ in range(0, 4):
            subject_visit = helper.enroll_to_baseline(
                visit_schedule_name=visit_schedule.name, schedule_name="schedule"
            )
            self.subject_identifiers.append(subject_visit.subject_identifier)

    @staticmethod
    def register_actions():
        site_action_items.registry = {}

        class TestLtfuAction(LtfuAction):
            pass

        class EndOfStudyAction(BaseEndOfStudyAction):
            reference_model = "edc_ltfu.offschedule"
            admin_site_name = "edc_ltfu_admin"
            parent_action_names = (
                UNBLINDING_REVIEW_ACTION,
                DEATH_REPORT_ACTION,
                LTFU_ACTION,
            )

        site_action_items.register(TestLtfuAction)
        site_action_items.register(EndOfStudyAction)

    @override_settings(EDC_LTFU_MODEL_NAME="edc_ltfu.ltfu")
    def test_model_name(self):
        self.assertEqual(get_ltfu_model_name(), "edc_ltfu.ltfu")

    @override_settings(EDC_LTFU_MODEL_NAME="edc_ltfu.badboy")
    def test_bad_model_cls(self):
        self.assertRaises(LookupError, get_ltfu_model_cls)

    @override_settings(EDC_LTFU_MODEL_NAME="edc_ltfu.ltfu")
    def test_model_cls(self):
        self.assertEqual(get_ltfu_model_cls(), Ltfu)

    @override_settings(EDC_LTFU_MODEL_NAME="edc_ltfu.ltfu")
    def test_ltfu_creates_and_closes_action(self):
        self.register_actions()
        Ltfu.objects.create(
            subject_identifier=self.subject_identifiers[0],
            last_seen_datetime=timezone.now(),
            phone_attempts=3,
            home_visited=YES,
            ltfu_category="lost",
        )
        try:
            ActionItem.objects.get(
                subject_identifier=self.subject_identifiers[0],
                action_type__name=LTFU_ACTION,
                status=CLOSED,
            )
        except ObjectDoesNotExist:
            self.fail("ObjectDoesNotExist unexpectedly raised")
