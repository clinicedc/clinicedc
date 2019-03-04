from arrow.arrow import Arrow
from datetime import datetime
from dateutil.relativedelta import relativedelta, SU, MO, TU, WE, TH, FR, SA
from django.test import TestCase, tag
from django.test.utils import override_settings
from edc_utils import get_utcnow

from ..facility import Facility
from ..import_holidays import import_holidays
from ..models import Holiday


class TestFacility(TestCase):
    def setUp(self):
        self.facility = Facility(
            name="clinic", days=[MO, TU, WE, TH, FR], slots=[100, 100, 100, 100, 100]
        )
        import_holidays()

    def test_allowed_weekday(self):
        facility = Facility(
            name="clinic", days=[MO, TU, WE, TH, FR], slots=[100, 100, 100, 100, 100]
        )
        for suggested, available in [
            (MO, MO),
            (TU, TU),
            (WE, WE),
            (TH, TH),
            (FR, FR),
            (SA, MO),
            (SU, MO),
        ]:
            dt = get_utcnow() + relativedelta(weekday=suggested.weekday)
            rdate = facility.available_rdate(dt, include_holidays=True)
            self.assertEqual(available.weekday, rdate.weekday())

    def test_allowed_weekday_limited(self):
        facility = Facility(name="clinic", days=[TU, TH], slots=[100, 100])
        for suggested, available in [
            (MO, TU),
            (TU, TU),
            (WE, TH),
            (TH, TH),
            (FR, TU),
            (SA, TU),
            (SU, TU),
        ]:
            dt = get_utcnow() + relativedelta(weekday=suggested.weekday)
            self.assertEqual(
                available.weekday,
                facility.available_rdate(dt, include_holidays=True).datetime.weekday(),
            )

    def test_allowed_weekday_limited2(self):
        facility = Facility(name="clinic", days=[TU, WE, TH], slots=[100, 100, 100])
        for suggested, available in [
            (MO, TU),
            (TU, TU),
            (WE, WE),
            (TH, TH),
            (FR, TU),
            (SA, TU),
            (SU, TU),
        ]:
            dt = get_utcnow() + relativedelta(weekday=suggested.weekday)
            self.assertEqual(
                available.weekday,
                facility.available_rdate(dt, include_holidays=True).datetime.weekday(),
            )

    def test_available_rdate(self):
        """Asserts finds available_rdate on first clinic day after holiday.
        """
        facility = Facility(name="clinic", days=[WE], slots=[100])
        suggested_date = get_utcnow() + relativedelta(months=3)
        available_rdate = facility.available_rdate(suggested_date)
        self.assertEqual(available_rdate.datetime.weekday(), WE.weekday)  # noqa

    def test_available_rdate_with_holiday(self):
        """Asserts finds available_rdate on first clinic day after holiday.
        """
        suggested_date = Arrow.fromdatetime(datetime(2017, 1, 1)).datetime
        expected_date = Arrow.fromdatetime(datetime(2017, 1, 8)).datetime
        facility = Facility(name="clinic", days=[suggested_date.weekday()], slots=[100])
        available_rdate = facility.available_rdate(suggested_date)
        self.assertEqual(expected_date, available_rdate.datetime)

    @override_settings(HOLIDAY_FILE=None)
    def test_read_holidays_from_db(self):
        """Asserts finds available_rdate on first clinic day after holiday.
        """
        suggested_date = Arrow.fromdatetime(datetime(2017, 1, 1)).datetime
        expected_date = Arrow.fromdatetime(datetime(2017, 1, 8)).datetime
        Holiday.objects.create(local_date=suggested_date)
        facility = Facility(name="clinic", days=[suggested_date.weekday()], slots=[100])
        available_rdate = facility.available_rdate(suggested_date)
        self.assertEqual(expected_date, available_rdate.datetime)
