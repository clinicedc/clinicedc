from datetime import datetime
from zoneinfo import ZoneInfo

from dateutil.relativedelta import FR, MO, SA, SU, TH, TU, WE, relativedelta
from django.test import TestCase
from django.test.utils import override_settings
from edc_sites import add_or_update_django_sites
from edc_sites.tests import SiteTestCaseMixin
from edc_utils import get_utcnow

from edc_facility.facility import Facility
from edc_facility.import_holidays import import_holidays
from edc_facility.models import Holiday


class TestFacility(SiteTestCaseMixin, TestCase):
    def setUp(self):
        add_or_update_django_sites(sites=self.default_sites)

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
            rdate = facility.available_arr(dt, schedule_on_holidays=True)
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
                facility.available_arr(dt, schedule_on_holidays=True).datetime.weekday(),
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
                facility.available_arr(dt, schedule_on_holidays=True).datetime.weekday(),
            )

    def test_available_arr(self):
        """Asserts finds available_arr on first clinic day after holiday."""
        facility = Facility(name="clinic", days=[WE], slots=[100])
        suggested_date = get_utcnow() + relativedelta(months=3)
        available_arr = facility.available_arr(suggested_date)
        self.assertEqual(available_arr.datetime.weekday(), WE.weekday)  # noqa

    def test_available_arr_with_holiday(self):
        """Asserts finds available_arr on first clinic day after holiday."""
        suggested_date = datetime(2017, 1, 1, tzinfo=ZoneInfo("UTC"))
        expected_date = datetime(2017, 1, 8, tzinfo=ZoneInfo("UTC"))
        facility = Facility(name="clinic", days=[suggested_date.weekday()], slots=[100])
        available_arr = facility.available_arr(suggested_date)
        self.assertEqual(expected_date, available_arr.datetime)

    @override_settings(HOLIDAY_FILE=None)
    def test_read_holidays_from_db(self):
        """Asserts finds available_arr on first clinic day after holiday."""
        suggested_date = datetime(2017, 1, 1, tzinfo=ZoneInfo("UTC"))
        expected_date = datetime(2017, 1, 8, tzinfo=ZoneInfo("UTC"))
        Holiday.objects.create(local_date=suggested_date)
        facility = Facility(name="clinic", days=[suggested_date.weekday()], slots=[100])
        available_arr = facility.available_arr(suggested_date)
        self.assertEqual(expected_date, available_arr.datetime)
