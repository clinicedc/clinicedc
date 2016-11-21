import pytz

from dateutil.relativedelta import relativedelta, SU, MO, TU, WE, TH, FR, SA
from datetime import datetime, date, time

from django.test import TestCase
from django.utils import timezone
from django.conf import settings

from edc_constants.constants import YES
from edc_example.models import Appointment, SubjectConsent, Enrollment, RegisteredSubject
from edc_example.factories import SubjectConsentFactory

from .models import Holiday
from .facility import Facility

tz = pytz.timezone(settings.TIME_ZONE)


class TestAppointment(TestCase):

    def setUp(self):
        self.subject_consent = SubjectConsent.objects.create(
            consent_datetime=timezone.now() - relativedelta(weeks=2),
            identity='111211111',
            confirm_identity='111211111',
            is_literate=YES)

    def test_appointments_creation(self):
        """Test if appointment triggering method creates appointments."""
        Enrollment.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            schedule_name='schedule1')
        self.assertEqual(Appointment.objects.all().count(), 4)

    def test_appointments_dates_mo(self):
        """Test appointment datetimes are chronological."""
        for index, day in enumerate([MO, TU, WE, TH, FR, SA, SU]):
            subject_consent = SubjectConsent.objects.create(
                consent_datetime=timezone.now() - relativedelta(weeks=2),
                identity='11121111' + str(index),
                confirm_identity='11121111' + str(index),
                is_literate=YES)
            Enrollment.objects.create(
                subject_identifier=subject_consent.subject_identifier,
                report_datetime=timezone.now() - relativedelta(weekday=day(-1)),
                schedule_name='schedule1')
            appt_datetimes = [obj.appt_datetime for obj in Appointment.objects.all().order_by('appt_datetime')]
            last = None
            for appt_datetime in appt_datetimes:
                if not last:
                    last = appt_datetime
                else:
                    self.assertGreater(appt_datetime, last)
                    last = appt_datetime


class TestFacility(TestCase):

    def setUp(self):
        self.facility = Facility(name='clinic', days=[MO, TU, WE, TH, FR], slots=[100, 100, 100, 100, 100])
        self.subject_identifier = '111111111'
        self.registered_subject = RegisteredSubject.objects.create(subject_identifier=self.subject_identifier)
        self.subject_consent = SubjectConsentFactory(
            subject_identifier=self.subject_identifier,
            consent_datetime=timezone.now())

    def test_allowed_weekday(self):
        facility = Facility(name='clinic', days=[MO, TU, WE, TH, FR], slots=[100, 100, 100, 100, 100])
        for suggested, available in [(MO, MO), (TU, TU), (WE, WE), (TH, TH), (FR, FR), (SA, MO), (SU, MO)]:
            dt = timezone.now() + relativedelta(weekday=suggested.weekday)
            self.assertEqual(available.weekday, facility.available_datetime(dt, window_days=30).weekday())

    def test_allowed_weekday_limited(self):
        facility = Facility(name='clinic', days=[TU, TH], slots=[100, 100])
        for suggested, available in [(MO, TU), (TU, TU), (WE, TH), (TH, TH), (FR, TU), (SA, TU), (SU, TU)]:
            dt = timezone.now() + relativedelta(weekday=suggested.weekday)
            self.assertEqual(available.weekday, facility.available_datetime(dt, window_days=30).weekday())

    def test_allowed_weekday_limited2(self):
        facility = Facility(name='clinic', days=[TU, WE, TH], slots=[100, 100, 100])
        for suggested, available in [(MO, TU), (TU, TU), (WE, WE), (TH, TH), (FR, TU), (SA, TU), (SU, TU)]:
            dt = timezone.now() + relativedelta(weekday=suggested.weekday)
            self.assertEqual(available.weekday, facility.available_datetime(dt, window_days=30).weekday())

    def test_available_datetime(self):
        """Asserts finds available_datetime on first wednesday after suggested_date."""
        facility = Facility(name='clinic', days=[WE], slots=[100])
        suggested_date = timezone.now() + relativedelta(months=3)
        available_datetime = facility.available_datetime(suggested_date, window_days=30)
        self.assertEqual(available_datetime.weekday(), WE.weekday)

    def test_available_datetime_with_holiday(self):
        """Asserts finds available_datetime on first wednesday after holiday."""
        facility = Facility(name='clinic', days=[WE], slots=[100])
        suggested_date = timezone.now() + relativedelta(months=3)
        available_datetime1 = facility.available_datetime(suggested_date, window_days=30)
        self.assertEqual(available_datetime1.weekday(), WE.weekday)
        Holiday.objects.create(day=available_datetime1)
        available_datetime2 = facility.available_datetime(suggested_date, window_days=30)
        self.assertEqual(available_datetime2.weekday(), WE.weekday)
        self.assertGreater(available_datetime2, available_datetime1)
