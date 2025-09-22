import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.visit_schedules.visit_schedule_metadata.visit_schedule import (
    get_visit_schedule,
)
from django.apps import apps as django_apps
from django.conf import settings
from django.test import TestCase, override_settings, tag

from edc_consent import site_consents
from edc_constants.constants import MALE
from edc_facility.import_holidays import import_holidays
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

test_datetime = datetime(2019, 6, 11, 8, 00, tzinfo=ZoneInfo("UTC"))

skip_condition = "django_collect_offline.apps.AppConfig" not in settings.INSTALLED_APPS
skip_reason = "django_collect_offline not installed"
if not skip_condition:
    from django_collect_offline.models import OutgoingTransaction
    from django_collect_offline.tests import OfflineTestHelper

    from ...offline_models import offline_models

utc_tz = ZoneInfo("UTC")


@unittest.skip("2")
@tag("metadata")
@override_settings(SITE_ID=10)
@time_machine.travel(datetime(2019, 8, 11, 8, 00, tzinfo=utc_tz))
class TestNaturalKey(TestCase):
    exclude_models = [
        "edc_visit_schedule.onschedule",
        "clinicedc_tests.offschedule",
        "clinicedc_tests.subjectrequisition",
        "edc_visit_tracking.subjectvisit",
        "edc_offstudy.subjectoffstudy",
        "clinicedc_tests.crfthree",
        "clinicedc_tests.crffour",
        "clinicedc_tests.crffive",
        "clinicedc_tests.crfsix",
        "clinicedc_tests.crfseven",
    ]

    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        self.helper = Helper()
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(get_visit_schedule(consent_v1))

        # note crfs in visit schedule are all set to REQUIRED by default.
        _, self.schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_visit_schedule.onschedule"
        )

    @unittest.skipIf(skip_condition, skip_reason)
    def test_natural_key_attrs(self):
        offline_helper = OfflineTestHelper()
        offline_helper.offline_test_natural_key_attr(
            "clinicedc_tests", exclude_models=self.exclude_models
        )

    @unittest.skipIf(skip_condition, skip_reason)
    def test_get_by_natural_key_attr(self):
        offline_helper = OfflineTestHelper()
        offline_helper.offline_test_get_by_natural_key_attr(
            "clinicedc_tests", exclude_models=self.exclude_models
        )

    @unittest.skipIf(skip_condition, skip_reason)
    def test_offline_test_natural_keys(self):
        offline_helper = OfflineTestHelper()
        self.helper.enroll_to_baseline(gender=MALE)
        model_objs = []
        completed_model_objs = {}
        completed_model_lower = []
        for outgoing_transaction in OutgoingTransaction.objects.all():
            if outgoing_transaction.tx_name in offline_models:
                model_cls = django_apps.get_app_config("edc_metadata").get_model(
                    outgoing_transaction.tx_name.split(".")[1]
                )
                obj = model_cls.objects.get(pk=outgoing_transaction.tx_pk)
                if outgoing_transaction.tx_name in completed_model_lower:
                    continue
                model_objs.append(obj)
                completed_model_lower.append(outgoing_transaction.tx_name)
        completed_model_objs.update({"edc_metadata": model_objs})
        offline_helper.offline_test_natural_keys(completed_model_objs)
