from arrow.arrow import Arrow
from datetime import datetime, date
from dateutil.relativedelta import relativedelta, SU, MO, TU, WE, TH, FR, SA
from django.test import TestCase, tag
from django.test.utils import override_settings
from edc_base.utils import get_utcnow

from ..facility import Facility
from ..models import Holiday


class TestFacility(TestCase):

    def setUp(self):
        self.facility = Facility(
            name='clinic', days=[MO, TU, WE, TH, FR], slots=[100, 100, 100, 100, 100])

    def test_allowed_weekday(self):
        facility = Facility(
            name='clinic',
            days=[MO, TU, WE, TH, FR], slots=[100, 100, 100, 100, 100])
        for suggested, available in [(MO, MO), (TU, TU), (WE, WE), (TH, TH), (FR, FR), (SA, MO), (SU, MO)]:
            dt = get_utcnow() + relativedelta(weekday=suggested.weekday)
            self.assertEqual(
                available.weekday, facility.available_datetime(dt).weekday())

    def test_allowed_weekday_limited(self):
        facility = Facility(name='clinic', days=[TU, TH], slots=[100, 100])
        for suggested, available in [(MO, TU), (TU, TU), (WE, TH), (TH, TH), (FR, TU), (SA, TU), (SU, TU)]:
            dt = get_utcnow() + relativedelta(weekday=suggested.weekday)
            self.assertEqual(
                available.weekday, facility.available_datetime(dt).weekday())

    def test_allowed_weekday_limited2(self):
        facility = Facility(
            name='clinic', days=[TU, WE, TH], slots=[100, 100, 100])
        for suggested, available in [(MO, TU), (TU, TU), (WE, WE), (TH, TH), (FR, TU), (SA, TU), (SU, TU)]:
            dt = get_utcnow() + relativedelta(weekday=suggested.weekday)
            self.assertEqual(
                available.weekday, facility.available_datetime(dt).weekday())

    def test_available_datetime(self):
        """Asserts finds available_datetime on first wednesday
        after suggested_date.
        """
        facility = Facility(name='clinic', days=[WE], slots=[100])
        suggested_date = get_utcnow() + relativedelta(months=3)
        available_datetime = facility.available_datetime(suggested_date)
        self.assertEqual(available_datetime.weekday(), WE.weekday)

    def test_available_datetime_with_holiday(self):
        """Asserts finds available_datetime on first wednesday
        after holiday.
        """
        suggested_date = Arrow.fromdatetime(datetime(2017, 1, 1)).datetime
        expected_date = Arrow.fromdatetime(datetime(2017, 1, 8)).datetime
        facility = Facility(
            name='clinic', days=[suggested_date.weekday()], slots=[100])
        available_datetime = facility.available_datetime(suggested_date)
        self.assertEqual(expected_date, available_datetime)

    @override_settings(HOLIDAY_FILE=None)
    def test_read_holidays_from_db(self):
        """Asserts finds available_datetime on first wednesday after holiday.
        """
        Holiday.objects.create(day=date(2017, 1, 1))
        suggested_date = Arrow.fromdatetime(datetime(2017, 1, 1)).datetime
        expected_date = Arrow.fromdatetime(datetime(2017, 1, 8)).datetime
        facility = Facility(
            name='clinic', days=[suggested_date.weekday()], slots=[100])
        available_datetime = facility.available_datetime(suggested_date)
        self.assertEqual(expected_date, available_datetime)
