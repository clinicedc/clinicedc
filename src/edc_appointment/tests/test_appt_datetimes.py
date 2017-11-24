import arrow

from datetime import datetime
from dateutil.relativedelta import relativedelta, SU, MO, TU, WE, TH, FR, SA, weekday
from django.apps import apps as django_apps
from django.test import TestCase, tag
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ..models import Appointment
from .helper import Helper
from .visit_schedule import visit_schedule1


class TestApptDatetimes(TestCase):

    helper_cls = Helper

    """Note: visit schedule has appointments on days 0, 1, 2, 3, etc.
    Default facility accepts appointments any day of the week.
    """

    def setUp(self):
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)

    def get_appt_datetimes(self, base_appt_datetime=None, subject_identifier=None):
        now = arrow.Arrow.fromdatetime(
            base_appt_datetime, tzinfo='UTC').datetime
        self.helper = self.helper_cls(
            subject_identifier=subject_identifier, now=now)
        self.helper.consent_and_enroll()
        appointments = Appointment.objects.filter(
            subject_identifier=subject_identifier)
        return [obj.appt_datetime for obj in appointments]

    @tag('1')
    def test_appointments_creation_dates(self):
        """Assert does not skip any days regardless of
        base appointment day.

        default facility accepts appointments any day of the week
        """
        for i in range(0, 7):
            subject_identifier = f'12345{i}'
            dt = datetime(2017, 1, 7 + i)
            now = arrow.Arrow.fromdatetime(dt, tzinfo='UTC').datetime
            self.helper = self.helper_cls(
                subject_identifier=subject_identifier, now=now)
            self.helper.consent_and_enroll()
            appointments = Appointment.objects.filter(
                subject_identifier=subject_identifier)
            appt_datetimes = [obj.appt_datetime for obj in appointments]
            base_appt_datetime = appt_datetimes[0]
            for index, appt_datetime in enumerate(appt_datetimes):
                self.assertEqual(
                    base_appt_datetime + relativedelta(days=index), appt_datetime)

    @tag('1')
    def test_appointments_creation_dates2(self):
        """Assert skips SA, SU.
        """
        django_apps.app_configs['edc_facility'].definitions = {
            'clinic': dict(days=[MO, TU, WE, TH, FR],
                           slots=[100, 100, 100, 100, 100])}
        base_appt_datetime = datetime(2017, 1, 7)
        self.assertTrue(weekday(base_appt_datetime.weekday()), SA)
        appt_datetimes = self.get_appt_datetimes(
            base_appt_datetime=base_appt_datetime,
            subject_identifier=f'123456')
        self.assertTrue(weekday(appt_datetimes[0].weekday()), MO)
        self.assertTrue(weekday(appt_datetimes[1].weekday()), TU)
        self.assertTrue(weekday(appt_datetimes[2].weekday()), WE)
        self.assertTrue(weekday(appt_datetimes[3].weekday()), TH)

        base_appt_datetime = datetime(2017, 1, 8)
        self.assertTrue(weekday(base_appt_datetime.weekday()), SU)
        appt_datetimes = self.get_appt_datetimes(
            base_appt_datetime=base_appt_datetime,
            subject_identifier=f'1234567')
        self.assertTrue(weekday(appt_datetimes[0].weekday()), MO)
        self.assertTrue(weekday(appt_datetimes[1].weekday()), TU)
        self.assertTrue(weekday(appt_datetimes[2].weekday()), WE)
        self.assertTrue(weekday(appt_datetimes[3].weekday()), TH)

        base_appt_datetime = datetime(2017, 1, 9)
        self.assertTrue(weekday(base_appt_datetime.weekday()), MO)
        appt_datetimes = self.get_appt_datetimes(
            base_appt_datetime=base_appt_datetime,
            subject_identifier=f'12345678')
        self.assertTrue(weekday(appt_datetimes[0].weekday()), MO)
        self.assertTrue(weekday(appt_datetimes[1].weekday()), TU)
        self.assertTrue(weekday(appt_datetimes[2].weekday()), WE)
        self.assertTrue(weekday(appt_datetimes[3].weekday()), TH)

        base_appt_datetime = datetime(2017, 1, 10)
        self.assertTrue(weekday(base_appt_datetime.weekday()), TU)
        appt_datetimes = self.get_appt_datetimes(
            base_appt_datetime=base_appt_datetime,
            subject_identifier=f'123456789')
        self.assertTrue(weekday(appt_datetimes[0].weekday()), TU)
        self.assertTrue(weekday(appt_datetimes[1].weekday()), WE)
        self.assertTrue(weekday(appt_datetimes[2].weekday()), TH)
        self.assertTrue(weekday(appt_datetimes[3].weekday()), FR)

        base_appt_datetime = datetime(2017, 1, 10)
        self.assertTrue(weekday(base_appt_datetime.weekday()), TU)
        appt_datetimes = self.get_appt_datetimes(
            base_appt_datetime=base_appt_datetime,
            subject_identifier=f'1234567890')
        self.assertTrue(weekday(appt_datetimes[0].weekday()), WE)
        self.assertTrue(weekday(appt_datetimes[1].weekday()), TH)
        self.assertTrue(weekday(appt_datetimes[2].weekday()), FR)
        self.assertTrue(weekday(appt_datetimes[3].weekday()), MO)
