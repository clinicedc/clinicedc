from __future__ import annotations

import datetime as dt
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.test import TestCase, override_settings, tag
from edc_consent import site_consents
from edc_facility.import_holidays import import_holidays
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from edc_appointment.constants import INCOMPLETE_APPT
from edc_appointment.models import Appointment
from edc_appointment_app.consents import consent_v1
from edc_appointment_app.models import SubjectVisit
from edc_appointment_app.tests.appointment_app_test_case_mixin import (
    AppointmentAppTestCaseMixin,
)
from edc_appointment_app.visit_schedule import get_visit_schedule3

from ...creators import UnscheduledAppointmentCreator
from ..helper import Helper

utc_tz = ZoneInfo("UTC")


test_datetime = dt.datetime(2019, 6, 11, 8, 00, tzinfo=utc_tz)


@override_settings(SITE_ID=10)
@time_machine.travel(test_datetime)
class TestInsertUnscheduled(AppointmentAppTestCaseMixin, TestCase):
    helper_cls = Helper

    def setUp(self):
        self.subject_identifier = "12345"

        site_consents.registry = {}
        site_consents.register(consent_v1)

        site_visit_schedules._registry = {}
        self.visit_schedule = get_visit_schedule3(consent_v1)
        site_visit_schedules.register(self.visit_schedule)

        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier,
            now=test_datetime,
        )

        self.helper.consent_and_put_on_schedule(
            visit_schedule_name=self.visit_schedule.name,
            schedule_name="three_monthly_schedule",
        )
        appointments = Appointment.objects.filter(
            subject_identifier=self.subject_identifier,
        )
        self.assertEqual(appointments.count(), 5)

        appointment = Appointment.objects.get(timepoint=0.0)
        self.create_related_visit(appointment)
        appointment = Appointment.objects.get(timepoint=3.0)
        self.create_related_visit(appointment)
        appointment = Appointment.objects.get(timepoint=6.0)
        self.create_related_visit(appointment)
        appointment = Appointment.objects.get(timepoint=9.0)
        self.create_related_visit(appointment)
        appointment = Appointment.objects.get(timepoint=12.0)
        self.create_related_visit(appointment)

        self.appt_datetimes = [
            o.appt_datetime for o in Appointment.objects.all().order_by("appt_datetime")
        ]

    @classmethod
    def setUpTestData(cls):
        import_holidays()

    @staticmethod
    def create_unscheduled(appointment: Appointment, days: int = None):
        creator = UnscheduledAppointmentCreator(
            subject_identifier=appointment.subject_identifier,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            suggested_appt_datetime=appointment.appt_datetime + relativedelta(days=days),
            suggested_visit_code_sequence=appointment.visit_code_sequence + 1,
        )
        appointment = creator.appointment
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save_base(update_fields=["appt_status"])
        return appointment

    @staticmethod
    def get_visit_codes(by: str = None, visit_schedule_name: str | None = None, **kwargs):
        opts = dict(visit_schedule_name=visit_schedule_name)
        return [
            f"{o.visit_code}.{o.visit_code_sequence}"
            for o in Appointment.objects.filter(**opts).order_by(by)
        ]

    @tag("5")
    def test_insert_unscheduled_between_related_visits(self):

        appt1030 = Appointment.objects.get(
            visit_code="1030",
            visit_code_sequence=0,
            visit_schedule_name=self.visit_schedule.name,
        )

        appt = self.create_unscheduled(appt1030, days=2)
        self.create_related_visit(appt)
        appt = self.create_unscheduled(appt1030, days=3)
        self.create_related_visit(appt)
        appt = self.create_unscheduled(appt1030, days=4)
        self.create_related_visit(appt)
        appt = self.create_unscheduled(appt1030, days=6)
        self.create_related_visit(appt)
        appt = self.create_unscheduled(appt1030, days=7)
        self.create_related_visit(appt)
        appt = self.create_unscheduled(appt1030, days=8)
        self.create_related_visit(appt)

        visit_codes = self.get_visit_codes(
            by="appt_datetime",
            visit_schedule_name=self.visit_schedule.name,
        )

        # appointments
        self.assertEqual(
            [
                "1000.0",
                "1030.0",
                "1030.1",
                "1030.2",
                "1030.3",
                "1030.4",
                "1030.5",
                "1030.6",
                "1060.0",
                "1090.0",
                "1120.0",
            ],
            visit_codes,
        )

        # related subject_visit
        self.assertEqual(
            [
                "1000.0",
                "1030.0",
                "1030.1",
                "1030.2",
                "1030.3",
                "1030.4",
                "1030.5",
                "1030.6",
                "1060.0",
                "1090.0",
                "1120.0",
            ],
            [
                f"{o.visit_code}.{o.visit_code_sequence}"
                for o in Appointment.objects.filter(
                    visit_schedule_name=self.visit_schedule.name,
                ).order_by("appt_datetime")
                if getattr(o, "related_visit", None)
            ],
        )

        # insert an unscheduled appointment between 1030.3 and 1030.4
        self.create_unscheduled(appt1030, days=5)

        # appointments
        visit_codes = self.get_visit_codes(
            by="appt_datetime",
            visit_schedule_name=self.visit_schedule.name,
        )
        self.assertEqual(
            [
                "1000.0",
                "1030.0",
                "1030.1",
                "1030.2",
                "1030.3",
                "1030.4",
                "1030.5",
                "1030.6",
                "1030.7",
                "1060.0",
                "1090.0",
                "1120.0",
            ],
            visit_codes,
        )

        # related subject_visit
        self.assertEqual(
            [
                "1000.0: 1000.0",
                "1030.0: 1030.0",
                "1030.1: 1030.1",
                "1030.2: 1030.2",
                "1030.3: 1030.3",
                "1030.5: 1030.5",
                "1030.6: 1030.6",
                "1030.7: 1030.7",
                "1060.0: 1060.0",
                "1090.0: 1090.0",
                "1120.0: 1120.0",
            ],
            [
                f"{o.appointment.visit_code}.{o.appointment.visit_code_sequence}: "
                f"{o.visit_code}.{o.visit_code_sequence}"
                for o in SubjectVisit.objects.filter(
                    visit_schedule_name=self.visit_schedule.name,
                ).order_by("report_datetime")
            ],
        )
