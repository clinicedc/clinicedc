from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.forms import OffScheduleForm
from clinicedc_tests.helper import Helper
from clinicedc_tests.sites import all_sites
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from dateutil.relativedelta import relativedelta
from django.test import TestCase, override_settings, tag

from edc_consent.site_consents import site_consents
from edc_facility.import_holidays import import_holidays
from edc_sites.site import sites as site_sites
from edc_sites.tests import SiteTestCaseMixin
from edc_sites.utils import add_or_update_django_sites
from edc_utils import get_utcnow
from edc_visit_schedule.models import OnSchedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

utc_tz = ZoneInfo("UTC")


@tag("visit_schedule")
@time_machine.travel(datetime(2025, 7, 12, 8, 00, tzinfo=utc_tz))
@override_settings(SITE_ID=10)
class TestModels(SiteTestCaseMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules.loaded = False
        site_visit_schedules._registry = {}
        site_visit_schedules.register(get_visit_schedule(consent_v1))

    def setUp(self):
        helper = Helper()
        self.consent = helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            report_datetime=get_utcnow(),
        )

    def test_offschedule_ok(self):
        onschedule = OnSchedule.objects.get(subject_identifier=self.consent.subject_identifier)
        data = dict(
            subject_identifier=self.consent.subject_identifier,
            offschedule_datetime=onschedule.onschedule_datetime + relativedelta(months=1),
        )
        form = OffScheduleForm(data=data)
        form.is_valid()
