from datetime import datetime

import arrow
from django.test import TestCase, tag

from ..constants import DAYS
from ..scheduler import Period


@tag('timepoint')
class TestPeriodWorkingDays(TestCase):

    def test_period_timepoint1(self):
        start_datetime = arrow.Arrow.fromdatetime(
            datetime(2017, 8, 24)).datetime
        period = Period(
            start_datetime=start_datetime, unit=DAYS, duration=1)
        self.assertEqual(len(period.workdays), 1)

    def test_period_timepoint3(self):
        # duration 0 zero index based
        start_datetime = arrow.Arrow.fromdatetime(
            datetime(2017, 8, 31)).datetime
        expected_datetime = arrow.Arrow.fromdatetime(
            datetime(2017, 8, 31)).datetime
        expected_datetime1 = arrow.Arrow.fromdatetime(
            datetime(2017, 9, 1)).datetime
        period = Period(
            start_datetime=start_datetime, unit=DAYS, duration=2)
        self.assertEqual(period.workdays[0], expected_datetime)
        self.assertEqual(period.workdays[1], expected_datetime1)

    def test_period_timepoint5(self):
        start_datetime = arrow.Arrow.fromdatetime(
            datetime(2017, 8, 31)).datetime
        period = Period(
            start_datetime=start_datetime, unit=DAYS, duration=2)
        self.assertEqual(len(period.workdays), 2)
