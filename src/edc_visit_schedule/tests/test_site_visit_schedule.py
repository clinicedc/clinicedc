from django.test import TestCase, tag

from ..schedule import Schedule
from ..site_visit_schedules import site_visit_schedules, SiteVisitScheduleError
from ..site_visit_schedules import AlreadyRegisteredVisitSchedule
from ..visit_schedule import VisitSchedule
from .models import OnSchedule, OffSchedule


class TestSiteVisitSchedule(TestCase):
    def setUp(self):

        self.visit_schedule = VisitSchedule(
            name="visit_schedule",
            verbose_name="Visit Schedule",
            offstudy_model="edc_visit_schedule.subjectoffstudy",
            death_report_model="edc_visit_schedule.deathreport",
        )

    def test_register_no_schedules(self):
        site_visit_schedules._registry = {}
        self.assertRaises(
            SiteVisitScheduleError, site_visit_schedules.register, self.visit_schedule
        )

    def test_already_registered(self):
        site_visit_schedules._registry = {}
        schedule = Schedule(
            name="schedule",
            onschedule_model="edc_visit_schedule.onschedule",
            offschedule_model="edc_visit_schedule.offschedule",
            appointment_model="edc_appointment.appointment",
            consent_model="edc_visit_schedule.subjectconsent",
        )
        self.visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(self.visit_schedule)
        self.assertRaises(
            AlreadyRegisteredVisitSchedule,
            site_visit_schedules.register,
            self.visit_schedule,
        )


class TestSiteVisitSchedule1(TestCase):
    def setUp(self):

        self.visit_schedule = VisitSchedule(
            name="visit_schedule",
            verbose_name="Visit Schedule",
            offstudy_model="edc_visit_schedule.subjectoffstudy",
            death_report_model="edc_visit_schedule.deathreport",
        )

        self.schedule = Schedule(
            name="schedule",
            onschedule_model="edc_visit_schedule.onschedule",
            offschedule_model="edc_visit_schedule.offschedule",
            appointment_model="edc_appointment.appointment",
            consent_model="edc_visit_schedule.subjectconsent",
        )

        self.visit_schedule.add_schedule(self.schedule)

        self.visit_schedule_two = VisitSchedule(
            name="visit_schedule_two",
            verbose_name="Visit Schedule Two",
            offstudy_model="edc_visit_schedule.subjectoffstudy",
            death_report_model="edc_visit_schedule.deathreport",
        )

        self.schedule_two = Schedule(
            name="schedule_two",
            onschedule_model="edc_visit_schedule.onscheduletwo",
            offschedule_model="edc_visit_schedule.offscheduletwo",
            appointment_model="edc_appointment.appointment",
            consent_model="edc_visit_schedule.subjectconsent",
        )

        self.visit_schedule_two.add_schedule(self.schedule_two)

        site_visit_schedules._registry = {}
        site_visit_schedules.register(self.visit_schedule)
        site_visit_schedules.register(self.visit_schedule_two)

    def test_visit_schedules(self):
        self.assertIn(
            self.visit_schedule, site_visit_schedules.visit_schedules.values()
        )
        self.assertIn(
            self.visit_schedule_two, site_visit_schedules.visit_schedules.values()
        )

    def test_get_visit_schedules(self):
        """Asserts returns a dictionary of visit schedules.
        """
        self.assertEqual(len(site_visit_schedules.get_visit_schedules()), 2)

    def test_get_visit_schedule_by_name(self):
        visit_schedule_name = self.visit_schedule.name
        self.assertEqual(
            self.visit_schedule,
            site_visit_schedules.get_visit_schedule(visit_schedule_name),
        )

    def test_get_visit_schedule_by_name_raises(self):
        visit_schedule_name = "blahblah"
        self.assertRaises(
            SiteVisitScheduleError,
            site_visit_schedules.get_visit_schedule,
            visit_schedule_name,
        )

    def test_get_visit_schedule_by_name_raises2(self):
        visit_schedule_name = "blah."
        self.assertRaises(
            SiteVisitScheduleError,
            site_visit_schedules.get_visit_schedule,
            visit_schedule_name,
        )

    def test_get_visit_schedule_by_name_raises3(self):
        visit_schedule_name = ".blah"
        self.assertRaises(
            SiteVisitScheduleError,
            site_visit_schedules.get_visit_schedule,
            visit_schedule_name,
        )

    def test_get_schedule_by_onschedule_model(self):
        _, schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_visit_schedule.onschedule"
        )
        self.assertEqual(schedule.onschedule_model_cls, OnSchedule)

    def test_get_schedule_by_offschedule_model(self):
        _, schedule = site_visit_schedules.get_by_offschedule_model(
            "edc_visit_schedule.offschedule"
        )
        self.assertEqual(schedule.offschedule_model_cls, OffSchedule)
