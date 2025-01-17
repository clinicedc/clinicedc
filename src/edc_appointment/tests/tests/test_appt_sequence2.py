from __future__ import annotations

import datetime as dt
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.test import TestCase, override_settings, tag
from edc_consent import site_consents
from edc_facility.import_holidays import import_holidays
from edc_metadata.models import CrfMetadata
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from edc_appointment.constants import INCOMPLETE_APPT
from edc_appointment.models import Appointment
from edc_appointment_app.consents import consent_v1
from edc_appointment_app.tests.appointment_app_test_case_mixin import (
    AppointmentAppTestCaseMixin,
)
from edc_appointment_app.visit_schedule import get_visit_schedule1

from ...creators import UnscheduledAppointmentCreator
from ...utils import reset_visit_code_sequence_or_pass
from ..helper import Helper

utc_tz = ZoneInfo("UTC")


@override_settings(SITE_ID=10)
@time_machine.travel(dt.datetime(2019, 6, 11, 8, 00, tzinfo=utc_tz))
class TestMoveAppointment(AppointmentAppTestCaseMixin, TestCase):
    helper_cls = Helper

    def setUp(self):
        self.subject_identifier = "12345"
        site_visit_schedules._registry = {}
        self.visit_schedule = get_visit_schedule1()
        site_visit_schedules.register(self.visit_schedule)
        site_consents.registry = {}
        site_consents.register(consent_v1)
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier,
            now=ResearchProtocolConfig().study_open_datetime,
        )
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name=self.visit_schedule.name, schedule_name="schedule1"
        )
        appointments = Appointment.objects.filter(subject_identifier=self.subject_identifier)
        self.assertEqual(appointments.count(), 4)

        appointment = Appointment.objects.get(timepoint=0.0)
        self.create_related_visit(appointment)
        appointment = Appointment.objects.get(timepoint=1.0)
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
    def get_visit_codes(by: str = None, **kwargs):
        return [
            f"{o.visit_code}.{o.visit_code_sequence}"
            for o in Appointment.objects.all().order_by(by)
        ]

    @tag("4")
    def test_resequence_appointment_on_insert_between_two_unscheduled(self):

        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=0)
        self.assertEqual(self.create_unscheduled(appointment, days=2).visit_code_sequence, 1)
        self.assertEqual(self.create_unscheduled(appointment, days=4).visit_code_sequence, 2)
        self.assertEqual(self.create_unscheduled(appointment, days=5).visit_code_sequence, 3)

        self.assertEqual(
            ["1000.0", "1000.1", "1000.2", "1000.3", "2000.0", "3000.0", "4000.0"],
            self.get_visit_codes(by="appt_datetime"),
        )

        # insert an appt between 1000.1 and 1000.2
        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=1)
        appointment = UnscheduledAppointmentCreator(
            subject_identifier=appointment.subject_identifier,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code="1000",
            facility=appointment.facility,
            suggested_appt_datetime=appointment.appt_datetime + relativedelta(days=1),
            suggested_visit_code_sequence=2,
        )
        self.assertEqual(appointment.visit_code_sequence, 2)

        self.assertEqual(
            ["1000.0", "1000.1", "1000.2", "1000.3", "1000.4", "2000.0", "3000.0", "4000.0"],
            self.get_visit_codes(by="appt_datetime"),
        )

    @tag("4")
    def test_repair_visit_code_sequences(self):
        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=0)
        self.create_unscheduled(appointment, days=2)
        appt2 = self.create_unscheduled(appointment, days=4)
        appt3 = self.create_unscheduled(appointment, days=5)

        appt2.visit_code_sequence = 3333
        appt2.save_base(update_fields=["visit_code_sequence"])

        appt3.visit_code_sequence = 33
        appt3.save_base(update_fields=["visit_code_sequence"])

        self.assertEqual(
            ["1000.0", "1000.1", "1000.3333", "1000.33", "2000.0", "3000.0", "4000.0"],
            self.get_visit_codes(by="appt_datetime"),
        )

        reset_visit_code_sequence_or_pass(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name="schedule1",
            visit_code="1000",
        )

        self.assertEqual(
            ["1000.0", "1000.1", "1000.2", "1000.3", "2000.0", "3000.0", "4000.0"],
            self.get_visit_codes(by="appt_datetime"),
        )

    @tag("4")
    def test_repair_visit_code_sequences_with_related_visit(self):
        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=0)
        appt1 = self.create_unscheduled(appointment, days=2)
        self.create_related_visit(appt1)
        appt2 = self.create_unscheduled(appointment, days=4)
        self.create_related_visit(appt2)
        appt3 = self.create_unscheduled(appointment, days=5)
        self.create_related_visit(appt3)

        appt2.visit_code_sequence = 3333
        appt2.save_base(update_fields=["visit_code_sequence"])
        appt2.related_visit.visit_code_sequence = 3333
        appt2.related_visit.save_base(update_fields=["visit_code_sequence"])

        appt3.visit_code_sequence = 33
        appt3.save_base(update_fields=["visit_code_sequence"])
        appt2.related_visit.visit_code_sequence = 33
        appt2.related_visit.save_base(update_fields=["visit_code_sequence"])

        self.assertEqual(
            ["1000.0", "1000.1", "1000.3333", "1000.33", "2000.0", "3000.0", "4000.0"],
            self.get_visit_codes(by="appt_datetime"),
        )

        reset_visit_code_sequence_or_pass(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name="schedule1",
            visit_code="1000",
        )

        self.assertEqual(
            ["1000.0", "1000.1", "1000.2", "1000.3", "2000.0", "3000.0", "4000.0"],
            self.get_visit_codes(by="appt_datetime"),
        )

        self.assertEqual(
            ["1000.0", "1000.1", "1000.2", "1000.3", "2000.0"],
            [
                f"{o.visit_code}.{o.visit_code_sequence}"
                for o in Appointment.objects.all().order_by("appt_datetime")
                if getattr(o, "related_visit", None)
            ],
        )

    @tag("4")
    def test_repair_visit_code_sequences_with_metadata(self):
        appointment = Appointment.objects.get(visit_code="1000", visit_code_sequence=0)
        appt1 = self.create_unscheduled(appointment, days=2)
        self.create_related_visit(appt1)
        appt2 = self.create_unscheduled(appointment, days=4)
        self.create_related_visit(appt2)
        appt3 = self.create_unscheduled(appointment, days=5)
        self.create_related_visit(appt3)

        appt2.visit_code_sequence = 3333
        appt2.save_base(update_fields=["visit_code_sequence"])
        appt2.related_visit.visit_code_sequence = 3333
        appt2.related_visit.save_base(update_fields=["visit_code_sequence"])
        CrfMetadata.objects.filter(visit_code="1000", visit_code_sequence=2).update(
            visit_code_sequence=3333
        )

        appt3.visit_code_sequence = 33
        appt3.save_base(update_fields=["visit_code_sequence"])
        appt2.related_visit.visit_code_sequence = 33
        appt2.related_visit.save_base(update_fields=["visit_code_sequence"])
        CrfMetadata.objects.filter(visit_code="1000", visit_code_sequence=3).update(
            visit_code_sequence=33
        )

        self.assertEqual(
            CrfMetadata.objects.filter(visit_code="1000", visit_code_sequence=3333).count(), 3
        )
        self.assertEqual(
            CrfMetadata.objects.filter(visit_code="1000", visit_code_sequence=33).count(), 3
        )
        reset_visit_code_sequence_or_pass(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name="schedule1",
            visit_code="1000",
        )
        self.assertEqual(
            CrfMetadata.objects.filter(visit_code="1000", visit_code_sequence=3333).count(), 0
        )
        self.assertEqual(
            CrfMetadata.objects.filter(visit_code="1000", visit_code_sequence=33).count(), 0
        )

        self.assertEqual(
            CrfMetadata.objects.filter(visit_code="1000", visit_code_sequence=2).count(), 3
        )
        self.assertEqual(
            CrfMetadata.objects.filter(visit_code="1000", visit_code_sequence=3).count(), 3
        )
