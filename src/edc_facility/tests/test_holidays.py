import arrow

from datetime import datetime
from django.test import TestCase, tag
from django.contrib.auth.models import User

from ..holidays import Holidays


class TestHolidays(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='erik')
        self.user.userprofile.country = 'botswana'
        self.user.userprofile.save()

    def test_repr(self):
        holidays = Holidays()
        self.assertTrue(repr(holidays))

    def test_holidays(self):
        for country in [None, 'botswana']:
            with self.subTest(country=country):
                holidays = Holidays(country=country)
                self.assertIsNotNone(holidays.holidays)
                keys = list(holidays.holidays)
                self.assertGreater(len(keys), 0)

    def test_key_is_formatted_datestring(self):
        for country in [None, 'botswana']:
            with self.subTest(country=country):
                holidays = Holidays(country=country)
                keys = list(holidays.holidays)
                self.assertGreater(len(keys), 0)
                self.assertTrue(datetime.strptime(keys[0], '%Y-%m-%d'))

    def test_iteration(self):
        for country in [None, 'botswana']:
            with self.subTest(country=country):
                holidays = Holidays(country=country)
                for local_date, label in holidays:
                    self.assertTrue(datetime.strptime(local_date, '%Y-%m-%d'))
                    self.assertIsNotNone(label)

    def test_is_holiday(self):
        start_datetime = arrow.Arrow.fromdatetime(
            datetime(2017, 9, 30)).datetime
        for country in [None, 'botswana']:
            with self.subTest(country=country):
                obj = Holidays(country=country)
                self.assertTrue(obj.is_holiday(start_datetime))

    def test_is_not_holiday(self):
        utc_datetime = arrow.Arrow.fromdatetime(
            datetime(2017, 9, 30)).datetime
        holidays = Holidays(country='botswana')
        self.assertTrue(holidays.is_holiday(utc_datetime))
        key = utc_datetime.strftime('%Y-%m-%d')
        self.assertEqual(holidays.holidays.get(key), 'Botswana Day')
