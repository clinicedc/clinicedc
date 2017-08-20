from dateutil.relativedelta import relativedelta, SU, MO, TU, WE, TH, FR, SA
from django.test import TestCase, tag
from edc_base.utils import get_utcnow

from ..facility import Facility
from ..models import Holiday
from .helper import Helper


class TestFacility(TestCase):

    helper_cls = Helper

    def setUp(self):
        self.facility = Facility(
            name='clinic', days=[MO, TU, WE, TH, FR], slots=[100, 100, 100, 100, 100])
        self.subject_identifier = '111111111'
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier)
        self.helper.consent_and_enroll()

    def test_allowed_weekday(self):
        facility = Facility(
            name='clinic', days=[MO, TU, WE, TH, FR], slots=[100, 100, 100, 100, 100])
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

    @tag('me')
    def test_available_datetime(self):
        """Asserts finds available_datetime on first wednesday after suggested_date."""
        facility = Facility(name='clinic', days=[WE], slots=[100])
        suggested_date = get_utcnow() + relativedelta(months=3)
        available_datetime = facility.available_datetime(suggested_date)
        self.assertEqual(available_datetime.weekday(), WE.weekday)

    def test_available_datetime_with_holiday(self):
        """Asserts finds available_datetime on first wednesday after holiday."""
        facility = Facility(name='clinic', days=[WE], slots=[100])
        suggested_date = get_utcnow() + relativedelta(months=3)
        if suggested_date.weekday() == WE.weekday:
            suggested_date = suggested_date + relativedelta(days=1)
        available_datetime1 = facility.available_datetime(suggested_date)
        self.assertEqual(available_datetime1.weekday(), WE.weekday)
        Holiday.objects.create(day=available_datetime1)
        available_datetime2 = facility.available_datetime(suggested_date)
        self.assertEqual(available_datetime2.weekday(), WE.weekday)
        self.assertGreater(available_datetime2, available_datetime1)
