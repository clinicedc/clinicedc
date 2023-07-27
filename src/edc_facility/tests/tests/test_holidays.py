from datetime import datetime
from zoneinfo import ZoneInfo

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.utils import override_settings
from edc_sites import add_or_update_django_sites
from edc_sites.tests import SiteTestCaseMixin

from edc_facility.holidays import HolidayError, Holidays
from edc_facility.import_holidays import import_holidays


class TestHolidays(SiteTestCaseMixin, TestCase):
    def setUp(self):
        add_or_update_django_sites(sites=self.default_sites)
        self.user = User.objects.create(username="erik")
        import_holidays()

    def test_repr(self):
        holidays = Holidays()
        self.assertTrue(repr(holidays))

    def test_str(self):
        holidays = Holidays()
        self.assertTrue(str(holidays))

    def test_(self):
        self.assertTrue(Holidays())

    def test_holidays_with_country(self):
        holidays = Holidays()
        self.assertIsNotNone(holidays.local_dates)
        self.assertGreater(len(holidays), 0)

    @override_settings(COUNTRY="botswana")
    def test_holidays_from_settings(self):
        self.assertRaises(HolidayError, Holidays)

    def test_key_is_formatted_datestring(self):
        holidays = Holidays()
        self.assertGreater(len(holidays.local_dates), 0)
        self.assertTrue(datetime.strftime(holidays.local_dates[0], "%Y-%m-%d"))

    def test_is_holiday(self):
        start_datetime = datetime(2017, 9, 30, tzinfo=ZoneInfo("UTC"))
        obj = Holidays()
        self.assertTrue(obj.is_holiday(start_datetime))

    def test_is_not_holiday(self):
        utc_datetime = datetime(2017, 9, 30, tzinfo=ZoneInfo("UTC"))
        holidays = Holidays()
        self.assertTrue(holidays.is_holiday(utc_datetime))
