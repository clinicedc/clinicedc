from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from edc_consent.consent_definition import ConsentDefinition
from edc_consent.site_consents import site_consents
from edc_constants.constants import FEMALE, MALE
from edc_facility.import_holidays import import_holidays
from edc_facility.utils import get_facility
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_utils import get_utcnow
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_schedule.visit import Visit
from edc_visit_schedule.visit_schedule import VisitSchedule

from edc_appointment.creators import AppointmentCreator
from edc_appointment.models import Appointment
from edc_appointment.tests.helper import Helper

utc_tz = ZoneInfo("UTC")


@time_machine.travel(datetime(2019, 6, 11, 8, 00, tzinfo=utc_tz))
@override_settings(
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=datetime(2019, 6, 11, 8, 00, tzinfo=utc_tz),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=datetime(2024, 6, 11, 8, 00, tzinfo=utc_tz),
    SITE_ID=10,
)
class AppointmentCreatorTestCase(TestCase):
    helper_cls = Helper

    def setUp(self):
        self.study_open_datetime = ResearchProtocolConfig().study_open_datetime
        self.study_close_datetime = ResearchProtocolConfig().study_close_datetime
        self.consent_v1 = ConsentDefinition(
            "edc_appointment_app.subjectconsentv1",
            version="1",
            start=self.study_open_datetime,
            end=self.study_close_datetime,
            age_min=18,
            age_is_adult=18,
            age_max=64,
            gender=[MALE, FEMALE],
        )
        site_consents.registry = {}
        site_consents.register(self.consent_v1)

        site_visit_schedules._registry = {}
        self.subject_identifier = "12345"
        self.visit_schedule = VisitSchedule(
            name="visit_schedule",
            verbose_name="Visit Schedule",
            offstudy_model="edc_appointment_app.subjectoffstudy",
            death_report_model="edc_appointment_app.deathreport",
        )

        self.schedule = Schedule(
            name="schedule",
            onschedule_model="edc_appointment_app.onschedule",
            offschedule_model="edc_appointment_app.offschedule",
            appointment_model="edc_appointment.appointment",
            consent_definitions=[self.consent_v1],
        )

        self.visit1000 = Visit(
            code="1000",
            timepoint=0,
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="7-day-clinic",
        )

        self.visit1001 = Visit(
            code="1001",
            timepoint=1,
            rbase=relativedelta(days=14),
            rlower=relativedelta(days=1),  # one day before base
            rupper=relativedelta(days=6),
            facility_name="7-day-clinic",
        )

        self.visit1010 = Visit(
            code="1010",
            timepoint=2,
            rbase=relativedelta(days=28),
            rlower=relativedelta(days=6),  # one day before base
            rupper=relativedelta(days=6),
            facility_name="7-day-clinic",
        )
        self.schedule.add_visit(self.visit1000)
        self.schedule.add_visit(self.visit1001)
        self.schedule.add_visit(self.visit1010)
        self.visit_schedule.add_schedule(self.schedule)

        site_visit_schedules.register(self.visit_schedule)

        class Meta:
            label_lower = ""

        class DummyAppointmentObj:
            subject_identifier = self.subject_identifier
            visit_schedule = self.visit_schedule
            schedule = self.schedule
            facility = get_facility(name="7-day-clinic")
            _meta = Meta()

        self.model_obj = DummyAppointmentObj()

    def put_on_schedule(self, dt, consent_definition: ConsentDefinition | None = None):
        self.helper = self.helper_cls(subject_identifier=self.subject_identifier, now=dt)
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            report_datetime=dt,
            consent_definition=consent_definition,
        )


class TestAppointmentCreator(AppointmentCreatorTestCase):
    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super().setUpClass()

    def test_init(self):
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        self.put_on_schedule(get_utcnow())
        self.assertTrue(
            AppointmentCreator(
                subject_identifier=self.subject_identifier,
                visit_schedule_name=self.visit_schedule.name,
                schedule_name=self.schedule.name,
                visit=self.visit1000,
                timepoint_datetime=get_utcnow(),
            )
        )
        traveller.stop()

    def test_str(self):
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        self.put_on_schedule(get_utcnow())
        creator = AppointmentCreator(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit=self.visit1000,
            timepoint_datetime=get_utcnow(),
        )
        self.assertEqual(str(creator), self.subject_identifier)
        traveller.stop()

    def test_repr(self):
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        self.put_on_schedule(get_utcnow())
        creator = AppointmentCreator(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit=self.visit1000,
            timepoint_datetime=get_utcnow(),
        )
        self.assertTrue(creator)
        traveller.stop()

    def test_create(self):
        """test create appointment, avoids new years holidays"""
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        appt_datetime = get_utcnow()
        self.put_on_schedule(appt_datetime)
        creator = AppointmentCreator(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit=self.visit1000,
            timepoint_datetime=appt_datetime,
        )
        appointment = creator.appointment
        self.assertEqual(
            Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[0],
            appointment,
        )
        self.assertEqual(
            Appointment.objects.all()
            .order_by("timepoint", "visit_code_sequence")[0]
            .appt_datetime,
            appt_datetime,
        )

    def test_create_appt_moves_forward(self):
        """Assert appt datetime moves forward to avoid holidays"""
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()
        appt_datetime = get_utcnow()
        self.put_on_schedule(appt_datetime)
        creator = AppointmentCreator(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit=self.visit1000,
            timepoint_datetime=appt_datetime,
        )
        appointment = creator.appointment
        self.assertEqual(
            Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[0],
            appointment,
        )
        self.assertEqual(
            Appointment.objects.all()
            .order_by("timepoint", "visit_code_sequence")[0]
            .appt_datetime,
            appt_datetime,
        )
        traveller.stop()


class TestAppointmentCreator2(AppointmentCreatorTestCase):
    @override_settings(
        HOLIDAY_FILE=settings.BASE_DIR / "no_holidays.csv",
    )
    def test_create_no_holidays(self):
        """test create appointment, no holidays"""
        import_holidays()
        traveller = time_machine.travel(self.study_open_datetime)
        traveller.start()

        site_consents.registry = {}
        consent_definition = ConsentDefinition(
            "edc_appointment_app.subjectconsentv1",
            version="1",
            start=self.study_open_datetime,
            end=self.study_close_datetime,
            age_min=18,
            age_is_adult=18,
            age_max=64,
            gender=[MALE, FEMALE],
        )
        site_consents.register(consent_definition)
        self.put_on_schedule(get_utcnow(), consent_definition)

        appt_datetime = get_utcnow()
        expected_appt_datetime = get_utcnow() + relativedelta(days=1)
        creator = AppointmentCreator(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit=self.visit1000,
            timepoint_datetime=appt_datetime,
        )
        self.assertEqual(
            Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[0],
            creator.appointment,
        )
        self.assertEqual(
            Appointment.objects.all()
            .order_by("timepoint", "visit_code_sequence")[0]
            .appt_datetime.date(),
            expected_appt_datetime.date(),
        )

        appt_datetime = get_utcnow() + relativedelta(days=2)
        creator = AppointmentCreator(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit=self.visit1000,
            timepoint_datetime=appt_datetime,
        )
        self.assertEqual(
            Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[0],
            creator.appointment,
        )
        self.assertEqual(
            Appointment.objects.all()
            .order_by("timepoint", "visit_code_sequence")[0]
            .appt_datetime.date(),
            appt_datetime.date(),
        )
        traveller.stop()
