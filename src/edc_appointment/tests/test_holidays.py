from datetime import datetime

import arrow
from django.test import TestCase

from ..holidays import Holidays


class TestHolidays(TestCase):

    def test_repr(self):
        obj = Holidays()
        self.assertTrue(obj.__repr__())

    def test_holidays(self):
        obj = Holidays(country='botswana')
        self.assertTrue(obj.holidays)

    def test_is_holiday(self):
        start_datetime = arrow.Arrow.fromdatetime(
            datetime(2017, 9, 30)).datetime
        obj = Holidays(country='botswana')
        self.assertTrue(obj.is_holiday(start_datetime))
