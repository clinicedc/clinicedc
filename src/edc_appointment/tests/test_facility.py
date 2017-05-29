from dateutil.relativedelta import relativedelta, SU, MO, TU, WE, TH, FR, SA

from model_mommy import mommy

from django.test import TestCase, tag

from edc_base_test.mixins.dates_test_mixin import DatesTestMixin
from edc_registration.models import RegisteredSubject

from ..facility import Facility
from ..models import Holiday


class TestFacility(DatesTestMixin, TestCase):

    def setUp(self):
        self.facility = Facility(
            name='clinic', days=[MO, TU, WE, TH, FR], slots=[100, 100, 100, 100, 100])
        self.subject_identifier = '111111111'
        self.registered_subject = mommy.make(
            RegisteredSubject, subject_identifier=self.subject_identifier)
        self.subject_consent = mommy.make_recipe(
            'edc_example.subjectconsent',
            identity=self.subject_identifier,
            confirm_identity=self.subject_identifier,
            subject_identifier=self.subject_identifier,
            consent_datetime=self.get_utcnow())

    def test_allowed_weekday(self):
        facility = Facility(
            name='clinic', days=[MO, TU, WE, TH, FR], slots=[100, 100, 100, 100, 100])
        for suggested, available in [(MO, MO), (TU, TU), (WE, WE), (TH, TH), (FR, FR), (SA, MO), (SU, MO)]:
            dt = self.get_utcnow() + relativedelta(weekday=suggested.weekday)
            self.assertEqual(
                available.weekday, facility.available_datetime(dt).weekday())

    def test_allowed_weekday_limited(self):
        facility = Facility(name='clinic', days=[TU, TH], slots=[100, 100])
        for suggested, available in [(MO, TU), (TU, TU), (WE, TH), (TH, TH), (FR, TU), (SA, TU), (SU, TU)]:
            dt = self.get_utcnow() + relativedelta(weekday=suggested.weekday)
            self.assertEqual(
                available.weekday, facility.available_datetime(dt).weekday())

    def test_allowed_weekday_limited2(self):
        facility = Facility(
            name='clinic', days=[TU, WE, TH], slots=[100, 100, 100])
        for suggested, available in [(MO, TU), (TU, TU), (WE, WE), (TH, TH), (FR, TU), (SA, TU), (SU, TU)]:
            dt = self.get_utcnow() + relativedelta(weekday=suggested.weekday)
            self.assertEqual(
                available.weekday, facility.available_datetime(dt).weekday())

    @tag('me')
    def test_available_datetime(self):
        """Asserts finds available_datetime on first wednesday after suggested_date."""
        facility = Facility(name='clinic', days=[WE], slots=[100])
        suggested_date = self.get_utcnow() + relativedelta(months=3)
        available_datetime = facility.available_datetime(suggested_date)
        self.assertEqual(available_datetime.weekday(), WE.weekday)

    def test_available_datetime_with_holiday(self):
        """Asserts finds available_datetime on first wednesday after holiday."""
        facility = Facility(name='clinic', days=[WE], slots=[100])
        suggested_date = self.get_utcnow() + relativedelta(months=3)
        if suggested_date.weekday() == WE.weekday:
            suggested_date = suggested_date + relativedelta(days=1)
        available_datetime1 = facility.available_datetime(suggested_date)
        self.assertEqual(available_datetime1.weekday(), WE.weekday)
        Holiday.objects.create(day=available_datetime1)
        available_datetime2 = facility.available_datetime(suggested_date)
        self.assertEqual(available_datetime2.weekday(), WE.weekday)
        self.assertGreater(available_datetime2, available_datetime1)
