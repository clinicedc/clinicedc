from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.test import TestCase, tag

from ..schedule import Schedule
from ..site_visit_schedules import site_visit_schedules
from ..system_checks import visit_schedule_check
from ..visit_schedule import VisitSchedule
from ..visit import Visit, FormsCollection
from ..visit.crf import Crf


class TestSystemChecks(TestCase):
    def test_system_check(self):
        site_visit_schedules._registry = {}
        errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, "edc_visit_schedule.001")

    def test_visit_schedule_ok(self):
        site_visit_schedules._registry = {}
        visit_schedule = VisitSchedule(
            name="visit_schedule",
            verbose_name="Visit Schedule",
            offstudy_model="edc_visit_schedule.subjectoffstudy",
            death_report_model="edc_visit_schedule.deathreport",
        )
        schedule = Schedule(
            name="schedule",
            onschedule_model="edc_visit_schedule.onschedule",
            offschedule_model="edc_visit_schedule.offschedule",
            appointment_model="edc_appointment.appointment",
            consent_model="edc_visit_schedule.subjectconsent",
        )
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)
        errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(errors), 0)

    def test_visit_schedule_bad_model(self):
        site_visit_schedules._registry = {}
        visit_schedule = VisitSchedule(
            name="visit_schedule",
            verbose_name="Visit Schedule",
            offstudy_model="blah.subjectoffstudy",
            death_report_model="edc_visit_schedule.deathreport",
        )
        schedule = Schedule(
            name="schedule",
            onschedule_model="edc_visit_schedule.onschedule",
            offschedule_model="edc_visit_schedule.offschedule",
            appointment_model="edc_appointment.appointment",
            consent_model="edc_visit_schedule.subjectconsent",
        )
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)
        errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(errors), 1)
        self.assertEqual("edc_visit_schedule.visit_schedules", errors[0].id)

    def test_schedule_bad_model(self):
        site_visit_schedules._registry = {}
        visit_schedule = VisitSchedule(
            name="visit_schedule",
            verbose_name="Visit Schedule",
            offstudy_model="edc_visit_schedule.subjectoffstudy",
            death_report_model="edc_visit_schedule.deathreport",
        )
        schedule = Schedule(
            name="schedule",
            onschedule_model="edc_visit_schedule.onschedule",
            offschedule_model="edc_visit_schedule.offschedule",
            appointment_model="blah.appointment",
            consent_model="edc_visit_schedule.subjectconsent",
        )
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)
        errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(errors), 1)
        self.assertEqual("edc_visit_schedule.schedules", errors[0].id)

    def test_schedule_bad_crf_model(self):
        site_visit_schedules._registry = {}
        visit_schedule = VisitSchedule(
            name="visit_schedule",
            verbose_name="Visit Schedule",
            offstudy_model="edc_visit_schedule.subjectoffstudy",
            death_report_model="edc_visit_schedule.deathreport",
        )
        schedule = Schedule(
            name="schedule",
            onschedule_model="edc_visit_schedule.onschedule",
            offschedule_model="edc_visit_schedule.offschedule",
            appointment_model="edc_appointment.appointment",
            consent_model="edc_visit_schedule.subjectconsent",
        )
        crfs = FormsCollection(
            Crf(show_order=10, model="blah.CrfOne"),
            Crf(show_order=20, model="blah.CrfTwo"),
            Crf(show_order=30, model="blah.CrfThree"),
        )
        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)
        errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(errors), 1)
        self.assertEqual("edc_visit_schedule.visits", errors[0].id)
