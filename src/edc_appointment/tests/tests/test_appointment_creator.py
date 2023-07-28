import os
from datetime import datetime
from unittest import skip
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from edc_facility.import_holidays import import_holidays
from edc_facility.utils import get_facility
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow
from edc_visit_schedule import Schedule, Visit, VisitSchedule, site_visit_schedules

from edc_appointment.creators import AppointmentCreator
from edc_appointment.models import Appointment
from edc_appointment_app.models import OnSchedule


class AppointmentCreatorTestCase(TestCase):
    def setUp(self):
        Appointment.objects.all().delete()
        RegisteredSubject.objects.create(subject_identifier="12345")
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
            consent_model="edc_appointment_app.subjectconsent",
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

        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=self.visit_schedule)

        self.onschedule = OnSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=get_utcnow() - relativedelta(days=1),
        )

        class Meta:
            label_lower = ""

        class DummyAppointmentObj:
            subject_identifier = self.subject_identifier
            visit_schedule = self.visit_schedule
            schedule = self.schedule
            facility = get_facility(name="7-day-clinic")
            _meta = Meta()

        self.model_obj = DummyAppointmentObj()


class TestAppointmentCreator(AppointmentCreatorTestCase):
    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super().setUpClass()

    def test_init(self):
        self.assertTrue(
            AppointmentCreator(
                subject_identifier=self.subject_identifier,
                visit_schedule_name=self.visit_schedule.name,
                schedule_name=self.schedule.name,
                visit=self.visit1000,
                timepoint_datetime=get_utcnow(),
            )
        )

    def test_str(self):
        creator = AppointmentCreator(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit=self.visit1000,
            timepoint_datetime=get_utcnow(),
        )
        self.assertEqual(str(creator), self.subject_identifier)

    def test_repr(self):
        creator = AppointmentCreator(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit=self.visit1000,
            timepoint_datetime=get_utcnow(),
        )
        self.assertTrue(creator)

    def test_create(self):
        """test create appointment, avoids new years holidays"""
        appt_datetime = datetime(2017, 1, 1, tzinfo=ZoneInfo("UTC"))
        self.onschedule.onschedule_datetime = appt_datetime
        self.onschedule.save()
        creator = AppointmentCreator(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit=self.visit1000,
            timepoint_datetime=appt_datetime,
        )
        appointment = creator.appointment
        self.assertEqual(Appointment.objects.all()[0], appointment)
        self.assertEqual(
            Appointment.objects.all()[0].appt_datetime,
            datetime(2017, 1, 3, tzinfo=ZoneInfo("UTC")),
        )

    def test_create_appt_moves_forward(self):
        """Assert appt datetime moves forward to avoid holidays"""
        appt_datetime = datetime(2017, 1, 1, tzinfo=ZoneInfo("UTC"))
        self.onschedule.onschedule_datetime = appt_datetime
        self.onschedule.save()
        creator = AppointmentCreator(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit=self.visit1000,
            timepoint_datetime=appt_datetime,
        )
        appointment = creator.appointment
        self.assertEqual(Appointment.objects.all()[0], appointment)
        self.assertEqual(
            Appointment.objects.all()[0].appt_datetime,
            datetime(2017, 1, 3, tzinfo=ZoneInfo("UTC")),
        )

    @skip("what is this")
    def test_create_appt_with_lower_greater_than_zero(self):
        appt_datetime = datetime(2017, 1, 10, tzinfo=ZoneInfo("UTC"))
        self.onschedule.onschedule_datetime = appt_datetime
        self.onschedule.save()

        creator = AppointmentCreator(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit=self.visit1001,
            timepoint_datetime=appt_datetime,
        )
        appointment = Appointment.objects.get(visit_code=self.visit1001.code)
        self.assertEqual(
            Appointment.objects.get(visit_code=self.visit1001.code),
            creator.appointment,
        )
        self.assertEqual(
            appointment.appt_datetime,
            datetime(2017, 1, 10, tzinfo=ZoneInfo("UTC")),
        )

    @skip("what is this")
    def test_create_appt_with_lower_greater_than_zero2(self):
        appt_datetime = datetime(2017, 1, 10, tzinfo=ZoneInfo("UTC"))
        self.onschedule.onschedule_datetime = appt_datetime
        self.onschedule.save()

        creator = AppointmentCreator(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit=self.visit1010,
            timepoint_datetime=appt_datetime,
        )
        appointment = Appointment.objects.get(visit_code=self.visit1010.code)
        self.assertEqual(
            Appointment.objects.get(visit_code=self.visit1010.code),
            creator.appointment,
        )
        self.assertEqual(
            appointment.appt_datetime,
            datetime(2017, 1, 10, tzinfo=ZoneInfo("UTC")),
        )

    def test_raise_on_naive_datetime(self):
        appt_datetime = datetime(2017, 1, 1)
        self.onschedule.onschedule_datetime = datetime(2017, 1, 1, tzinfo=ZoneInfo("UTC"))
        self.onschedule.save()
        self.assertRaises(
            ValueError,
            AppointmentCreator,
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit=self.visit1000,
            timepoint_datetime=appt_datetime,
        )

    def test_raise_on_naive_datetime2(self):
        appt_datetime = datetime(2017, 1, 1)
        self.onschedule.onschedule_datetime = datetime(2017, 1, 1, tzinfo=ZoneInfo("UTC"))
        self.onschedule.save()
        self.assertRaises(
            ValueError,
            AppointmentCreator,
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit=self.visit1000,
            timepoint_datetime=appt_datetime,
        )


class TestAppointmentCreator2(AppointmentCreatorTestCase):
    @override_settings(
        HOLIDAY_FILE=os.path.join(
            settings.BASE_DIR, settings.APP_NAME, "tests", "no_holidays.csv"
        )
    )
    def test_create_no_holidays(self):
        """test create appointment, no holiday to avoid after 1900"""
        import_holidays()
        appt_datetime = datetime(1900, 1, 1, tzinfo=ZoneInfo("UTC"))
        self.onschedule.onschedule_datetime = appt_datetime
        self.onschedule.save()

        expected_appt_datetime = datetime(1900, 1, 2, tzinfo=ZoneInfo("UTC"))
        creator = AppointmentCreator(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit=self.visit1000,
            timepoint_datetime=appt_datetime,
        )
        self.assertEqual(Appointment.objects.all()[0], creator.appointment)
        self.assertEqual(Appointment.objects.all()[0].appt_datetime, expected_appt_datetime)

        appt_datetime = datetime(1900, 1, 3, tzinfo=ZoneInfo("UTC"))
        creator = AppointmentCreator(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit=self.visit1000,
            timepoint_datetime=appt_datetime,
        )
        self.assertEqual(Appointment.objects.all()[0], creator.appointment)
        self.assertEqual(Appointment.objects.all()[0].appt_datetime, appt_datetime)
