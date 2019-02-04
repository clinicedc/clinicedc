import arrow

from datetime import datetime
from django.test import TestCase, tag
from django.contrib.auth.models import User
from django.test.utils import override_settings

from ..import_holidays import import_holidays
from ..holidays import Holidays


class TestHolidays(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="erik")
        self.user.userprofile.country = "botswana"
        self.user.userprofile.save()
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
        holidays = Holidays(country="botswana")
        self.assertIsNotNone(holidays.local_dates)
        self.assertGreater(len(holidays), 0)

    @override_settings(COUNTRY="botswana")
    def test_holidays_from_settings(self):
        holidays = Holidays(country=None)
        self.assertIsNotNone(holidays.holidays)
        self.assertGreater(len(holidays), 0)

    def test_key_is_formatted_datestring(self):
        holidays = Holidays(country="botswana")
        self.assertGreater(len(holidays.local_dates), 0)
        self.assertTrue(datetime.strftime(holidays.local_dates[0], "%Y-%m-%d"))

    def test_is_holiday(self):
        start_datetime = arrow.Arrow.fromdatetime(datetime(2017, 9, 30)).datetime
        for country in [None, "botswana"]:
            with self.subTest(country=country):
                obj = Holidays(country=country)
                self.assertTrue(obj.is_holiday(start_datetime))

    def test_is_not_holiday(self):
        utc_datetime = arrow.Arrow.fromdatetime(datetime(2017, 9, 30)).datetime
        holidays = Holidays(country="botswana")
        self.assertTrue(holidays.is_holiday(utc_datetime))
