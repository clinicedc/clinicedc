from datetime import datetime

import arrow
from django.test import TestCase

from ..holidays.country import Country


class TestMoveToWorkingDay(TestCase):
    def test_move_to_workingday(self):
        start_datetime = arrow.Arrow.fromdatetime(datetime(2017, 9, 30)).datetime
        expected_datetime = arrow.Arrow.fromdatetime(datetime(2017, 10, 2)).datetime
        country = Country(skip_holiday=True, skip_weekend=True)
        self.assertEqual(
            country.move_to_workday(utc_datetime=start_datetime), expected_datetime
        )

    def test_skip_holiday_only(self):
        start_datetime = arrow.Arrow.fromdatetime(datetime(2017, 9, 30)).datetime
        expected_datetime = arrow.Arrow.fromdatetime(datetime(2017, 10, 1)).datetime
        country = Country(skip_holiday=True)
        self.assertEqual(
            country.move_to_workday(utc_datetime=start_datetime), expected_datetime
        )

    def test_skip_holiday_only1(self):
        start_datetime = arrow.Arrow.fromdatetime(datetime(2017, 9, 1)).datetime
        country = Country(skip_holiday=True, skip_weekend=True)
        self.assertEqual(
            country.move_to_workday(utc_datetime=start_datetime), start_datetime
        )
