from datetime import datetime
from zoneinfo import ZoneInfo

from clinicedc_tests.mixins import SiteTestCaseMixin
from clinicedc_tests.sites import all_sites
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.utils import override_settings, tag

from edc_facility.exceptions import FacilitySiteError
from edc_facility.holidays import Holidays
from edc_facility.import_holidays import import_holidays
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites


@tag("facility")
@override_settings(SITE_ID=10)
class TestHolidays(SiteTestCaseMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

    def setUp(self):
        self.user = User.objects.create(username="erik")

    @override_settings(SITE_ID=10)
    def test_repr(self):
        holidays = Holidays()
        self.assertTrue(repr(holidays))

    @override_settings(SITE_ID=10)
    def test_str(self):
        holidays = Holidays()
        self.assertTrue(str(holidays))

    @override_settings(SITE_ID=10)
    def test_(self):
        self.assertTrue(Holidays())

    @override_settings(SITE_ID=2)
    def test_bad_site(self):
        holidays = Holidays()
        self.assertRaises(FacilitySiteError, getattr, holidays, "site")

    @override_settings(SITE_ID=10)
    def test_holidays_with_country(self):
        holidays = Holidays()
        self.assertIsNotNone(holidays.local_dates)
        self.assertGreater(len(holidays), 0)

    @override_settings(SITE_ID=10)
    def test_key_is_formatted_datestring(self):
        holidays = Holidays()
        self.assertGreater(len(holidays.local_dates), 0)
        self.assertTrue(datetime.strftime(holidays.local_dates[0], "%Y-%m-%d"))

    @override_settings(SITE_ID=10)
    def test_is_holiday(self):
        start_datetime = datetime(2017, 9, 30, tzinfo=ZoneInfo("UTC"))
        obj = Holidays()
        self.assertTrue(obj.is_holiday(start_datetime))

    @override_settings(SITE_ID=10)
    def test_is_not_holiday(self):
        utc_datetime = datetime(2017, 9, 30, tzinfo=ZoneInfo("UTC"))
        holidays = Holidays()
        self.assertTrue(holidays.is_holiday(utc_datetime))
