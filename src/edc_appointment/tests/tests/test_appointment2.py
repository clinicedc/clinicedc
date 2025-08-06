from datetime import datetime
from decimal import Context
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import FR, MO, SA, SU, TH, TU, WE, relativedelta
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings
from edc_consent.site_consents import site_consents
from edc_facility.import_holidays import import_holidays
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED, UNSCHEDULED
from edc_visit_tracking.utils import get_related_visit_model_cls

from edc_appointment.constants import INCOMPLETE_APPT, SCHEDULED_APPT, UNSCHEDULED_APPT
from edc_appointment.exceptions import AppointmentDatetimeError
from edc_appointment.utils import get_appointment_model_cls, get_appt_reason_choices
from edc_appointment_app.consents import consent_v1
from edc_appointment_app.visit_schedule import get_visit_schedule1, get_visit_schedule2

from ..helper import Helper

utc_tz = ZoneInfo("UTC")


@override_settings(SITE_ID=10, EDC_SITES_REGISTER_DEFAULT=True)
@time_machine.travel(datetime(2019, 6, 11, 8, 00, tzinfo=utc_tz))
class TestAppointment(TestCase):
    helper_cls = Helper

    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        self.subject_identifier = "12345"
        site_visit_schedules._registry = {}
        self.visit_schedule1 = get_visit_schedule1()
        self.visit_schedule2 = get_visit_schedule2()
        site_visit_schedules.register(self.visit_schedule1)
        site_visit_schedules.register(self.visit_schedule2)
        site_consents.registry = {}
        site_consents.register(consent_v1)
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier,
            now=ResearchProtocolConfig().study_open_datetime,
        )

    def test_appointments_dates_mo(self):
        """Test appointment datetimes are chronological."""
        for day in [MO, TU, WE, TH, FR, SA, SU]:
            helper = self.helper_cls(
                subject_identifier=f"{self.subject_identifier}-{day}",
                now=ResearchProtocolConfig().study_open_datetime,
            )
            subject_consent = helper.consent_and_put_on_schedule(
                visit_schedule_name=self.visit_schedule1.name,
                schedule_name="schedule1",
                report_datetime=get_utcnow(),
                onschedule_datetime=get_utcnow()
                + relativedelta(weeks=2)
                + relativedelta(weekday=day(-1)),
            )
            appt_datetimes = [
                obj.appt_datetime
                for obj in get_appointment_model_cls()
                .objects.filter(subject_identifier=subject_consent.subject_identifier)
                .order_by("appt_datetime")
            ]
            last = None
            self.assertGreater(len(appt_datetimes), 0)
            for appt_datetime in appt_datetimes:
                if not last:
                    last = appt_datetime
                else:
                    self.assertGreater(appt_datetime, last)
                    last = appt_datetime

    def test_attempt_to_change(self):
        for day in [MO, TU, WE, TH, FR, SA, SU]:
            helper = self.helper_cls(
                subject_identifier=f"{self.subject_identifier}-{day}",
                now=ResearchProtocolConfig().study_open_datetime,
            )
            subject_consent = helper.consent_and_put_on_schedule(
                visit_schedule_name=self.visit_schedule1.name,
                schedule_name="schedule1",
                report_datetime=get_utcnow(),
            )
        subject_identifier = subject_consent.subject_identifier
        self.assertEqual(
            get_appointment_model_cls()
            .objects.filter(subject_identifier=subject_identifier)
            .count(),
            4,
        )

        # create two unscheduled appts after first
        appointment0 = (
            get_appointment_model_cls()
            .objects.filter(subject_identifier=subject_identifier)
            .order_by("appt_datetime")[0]
        )
        get_related_visit_model_cls().objects.create(
            appointment=appointment0,
            report_datetime=appointment0.appt_datetime,
            reason=SCHEDULED,
        )
        appointment0.appt_status = INCOMPLETE_APPT
        appointment0.save()

        appointment0_1 = self.helper.add_unscheduled_appointment(appointment0)
        get_related_visit_model_cls().objects.create(
            appointment=appointment0_1,
            report_datetime=appointment0.appt_datetime,
            reason=UNSCHEDULED,
        )
        appointment0_1.appt_status = INCOMPLETE_APPT
        appointment0_1.save()

        appointment0_2 = self.helper.add_unscheduled_appointment(appointment0_1)

        appointment0_1.appt_datetime = appointment0_2.appt_datetime + relativedelta(days=1)

        self.assertRaises(AppointmentDatetimeError, appointment0_1.save)

    def test_timepoint(self):
        """Assert timepoints are saved from the schedule correctly
        as Decimals and ordered by appt_datetime.
        """
        context = Context(prec=2)
        schedule_name = self.visit_schedule1.schedules.get("schedule1").name
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name=self.visit_schedule1.name, schedule_name=schedule_name
        )
        self.assertEqual(
            [
                obj.timepoint
                for obj in get_appointment_model_cls().objects.all().order_by("appt_datetime")
            ],
            [context.create_decimal(n) for n in range(0, 4)],
        )

    def test_first_appointment_with_visit_schedule(self):
        """Asserts first appointment correctly selected if just
        visit_schedule_name provided.
        """
        schedule_name = self.visit_schedule2.schedules.get("schedule2").name
        subject_consent = self.helper.consent_and_put_on_schedule(
            visit_schedule_name=self.visit_schedule2.name, schedule_name=schedule_name
        )

        schedule = self.visit_schedule1.schedules.get("schedule1")
        schedule.put_on_schedule(subject_consent.subject_identifier, get_utcnow())

        first_appointment = get_appointment_model_cls().objects.first_appointment(
            subject_identifier=self.subject_identifier,
            visit_schedule_name="visit_schedule2",
        )
        self.assertEqual(first_appointment.schedule_name, "schedule2")

        self.assertEqual(
            get_appointment_model_cls()
            .objects.filter(
                subject_identifier=self.subject_identifier,
                visit_schedule_name="visit_schedule2",
            )
            .order_by("appt_datetime")[0],
            first_appointment,
        )

    @override_settings(
        EDC_APPOINTMENT_APPT_REASON_CHOICES=((UNSCHEDULED_APPT, "Unscheduled"),)
    )
    def test_setting_reason_choices_invalid(self):
        self.assertRaises(ImproperlyConfigured, get_appt_reason_choices)

    @override_settings(
        EDC_APPOINTMENT_APPT_REASON_CHOICES=(
            (SCHEDULED_APPT, "Routine / Scheduled"),
            (UNSCHEDULED_APPT, "Unscheduled"),
        )
    )
    def test_setting_reason_choices_valid(self):
        try:
            choices = get_appt_reason_choices()
        except ImproperlyConfigured:
            self.fail("ImproperlyConfigured unexpectedly raised")
        self.assertEqual(
            choices,
            (
                (SCHEDULED_APPT, "Routine / Scheduled"),
                (UNSCHEDULED_APPT, "Unscheduled"),
            ),
        )

    @override_settings(
        EDC_APPOINTMENT_APPT_REASON_CHOICES=(
            (SCHEDULED_APPT, "Routine / Scheduled"),
            (UNSCHEDULED_APPT, "Unscheduled"),
            ("blah", "Blah"),
        )
    )
    def test_setting_reason_choices_valid2(self):
        try:
            choices = get_appt_reason_choices()
        except ImproperlyConfigured:
            self.fail("ImproperlyConfigured unexpectedly raised")
        self.assertEqual(
            choices,
            (
                (SCHEDULED_APPT, "Routine / Scheduled"),
                (UNSCHEDULED_APPT, "Unscheduled"),
                ("blah", "Blah"),
            ),
        )
