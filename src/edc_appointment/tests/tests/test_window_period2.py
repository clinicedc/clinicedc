import datetime as dt
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.test import TestCase, override_settings
from edc_facility import import_holidays
from edc_sites.tests import SiteTestCaseMixin
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from edc_appointment.models import Appointment
from edc_appointment.tests.helper import Helper
from edc_appointment.utils import (
    AppointmentDateWindowPeriodGapError,
    get_appointment_by_datetime,
    get_window_gap_days,
)
from edc_appointment_app.visit_schedule import get_visit_schedule4

utc = ZoneInfo("UTC")


@time_machine.travel(dt.datetime(2019, 7, 11, 8, 00, tzinfo=utc))
@override_settings(SITE_ID=10)
class TestAppointmentWindowPeriod2(SiteTestCaseMixin, TestCase):
    helper_cls = Helper

    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        self.subject_identifier = "12345"
        self.visit_schedule4 = get_visit_schedule4()
        self.schedule4 = self.visit_schedule4.schedules.get("three_monthly_schedule")
        site_visit_schedules._registry = {}
        site_visit_schedules.register(self.visit_schedule4)
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier,
            now=get_utcnow() - relativedelta(years=2),
        )

    @override_settings(EDC_VISIT_SCHEDULE_DEFAULT_MAX_VISIT_GAP_ALLOWED=0)
    def test_suggested_date_in_window_period_gap_raises(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name=self.visit_schedule4.name,
            schedule_name=self.schedule4.name,
        )
        appointments = Appointment.objects.filter(
            subject_identifier=self.subject_identifier
        ).order_by("appt_datetime")
        self.assertEqual(appointments.count(), 5)
        appointment_1000 = appointments[0]
        appointment_1060 = appointments[2]

        subject_identifier = appointment_1000.subject_identifier
        visit_schedule_name = appointment_1000.visit_schedule_name
        schedule_name = appointment_1000.schedule_name

        suggested_appt_datetime = (
            appointment_1060.appt_datetime
            - appointment_1060.visit.rlower
            - relativedelta(days=1)
        )
        with self.assertRaises(AppointmentDateWindowPeriodGapError) as cm:
            get_appointment_by_datetime(
                suggested_appt_datetime,
                subject_identifier,
                visit_schedule_name,
                schedule_name,
            )

        self.assertIn(
            "Date falls in a `window period gap` between 1030 and 1060", str(cm.exception)
        )

    @override_settings(EDC_VISIT_SCHEDULE_DEFAULT_MAX_VISIT_GAP_ALLOWED=7)
    def test_match_window_period_gap_adjusted(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name=self.visit_schedule4.name,
            schedule_name=self.schedule4.name,
        )
        appointments = Appointment.objects.filter(
            subject_identifier=self.subject_identifier
        ).order_by("appt_datetime")
        self.assertEqual(appointments.count(), 5)
        appointment_1000 = appointments[0]
        appointment_1060 = appointments[2]

        subject_identifier = appointment_1000.subject_identifier
        visit_schedule_name = appointment_1000.visit_schedule_name
        schedule_name = appointment_1000.schedule_name

        for days, in_adjusted_window in [
            (6, True),
            (7, True),
            (8, False),
            (9, False),
        ]:
            with self.subTest(days=days, in_adjusted_window=in_adjusted_window):
                suggested_appt_datetime = (
                    appointment_1060.appt_datetime
                    - appointment_1060.visit.rlower
                    - relativedelta(days=days)
                )
                try:
                    appointment = get_appointment_by_datetime(
                        suggested_appt_datetime,
                        subject_identifier,
                        visit_schedule_name,
                        schedule_name,
                        raise_if_in_gap=False,
                    )
                except AppointmentDateWindowPeriodGapError as e:
                    self.fail(
                        f"AppointmentDateWindowPeriodGapError unexpectedly raised. Got {e}"
                    )
                if not in_adjusted_window:
                    self.assertIsNone(appointment)
                else:
                    self.assertEqual("1060", appointment.visit_code)

    def test_past_last_visit(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name=self.visit_schedule4.name,
            schedule_name=self.schedule4.name,
        )
        appointments = Appointment.objects.filter(
            subject_identifier=self.subject_identifier
        ).order_by("appt_datetime")
        self.assertEqual(appointments.count(), 5)
        appointment_1000 = appointments[0]
        appointment_1120 = appointments[4]

        subject_identifier = appointment_1000.subject_identifier
        visit_schedule_name = appointment_1000.visit_schedule_name
        schedule_name = appointment_1000.schedule_name

        suggested_appt_datetime = (
            appointment_1120.appt_datetime
            + appointment_1120.visit.rupper
            + relativedelta(days=1)
        )
        try:
            appointment = get_appointment_by_datetime(
                suggested_appt_datetime,
                subject_identifier,
                visit_schedule_name,
                schedule_name,
                raise_if_in_gap=False,
            )
        except AppointmentDateWindowPeriodGapError as e:
            self.fail(f"AppointmentDateWindowPeriodGapError unexpectedly raised. Got {e}")
        self.assertIsNone(appointment)

    def test_window_gap_days(self):
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name=self.visit_schedule4.name,
            schedule_name=self.schedule4.name,
        )
        appointments = Appointment.objects.filter(
            subject_identifier=self.subject_identifier
        ).order_by("appt_datetime")
        appointment_1030 = appointments[1]
        gap_days = get_window_gap_days(appointment_1030)
        self.assertEqual(gap_days, 62)
