from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag
from edc_sites.tests import SiteTestCaseMixin
from edc_utils import get_utcnow

from ..models import SubjectScheduleHistory
from ..schedule import Schedule
from ..site_visit_schedules import site_visit_schedules
from ..subject_schedule import SubjectSchedule, SubjectScheduleError
from ..visit_schedule import VisitSchedule
from .models import SubjectConsent, OnSchedule, OffSchedule


class TestSubjectSchedule(SiteTestCaseMixin, TestCase):
    def setUp(self):
        site_visit_schedules._registry = {}
        self.visit_schedule = VisitSchedule(
            name="visit_schedule",
            verbose_name="Visit Schedule",
            offstudy_model="edc_visit_schedule.SubjectOffstudy",
            death_report_model="edc_visit_schedule.DeathReport",
        )

        self.schedule = Schedule(
            name="schedule",
            onschedule_model="edc_visit_schedule.OnSchedule",
            offschedule_model="edc_visit_schedule.OffSchedule",
            appointment_model="edc_appointment.appointment",
            consent_model="edc_visit_schedule.subjectconsent",
        )
        self.schedule3 = Schedule(
            name="schedule_three",
            onschedule_model="edc_visit_schedule.OnScheduleThree",
            offschedule_model="edc_visit_schedule.OffScheduleThree",
            appointment_model="edc_appointment.appointment",
            consent_model="edc_visit_schedule.subjectconsent",
        )

        self.visit_schedule.add_schedule(self.schedule)
        self.visit_schedule.add_schedule(self.schedule3)
        site_visit_schedules.register(self.visit_schedule)

        self.visit_schedule_two = VisitSchedule(
            name="visit_schedule_two",
            verbose_name="Visit Schedule Two",
            offstudy_model="edc_visit_schedule.SubjectOffstudy",
            death_report_model="edc_visit_schedule.DeathReport",
        )

        self.schedule_two_1 = Schedule(
            name="schedule_two",
            onschedule_model="edc_visit_schedule.OnScheduleTwo",
            offschedule_model="edc_visit_schedule.OffScheduleTwo",
            appointment_model="edc_appointment.appointment",
            consent_model="edc_visit_schedule.subjectconsent",
        )
        self.schedule_two_2 = Schedule(
            name="schedule_four",
            onschedule_model="edc_visit_schedule.OnScheduleFour",
            offschedule_model="edc_visit_schedule.OffScheduleFour",
            appointment_model="edc_appointment.appointment",
            consent_model="edc_visit_schedule.subjectconsent",
        )

        self.visit_schedule_two.add_schedule(self.schedule_two_1)
        self.visit_schedule_two.add_schedule(self.schedule_two_2)
        site_visit_schedules.register(self.visit_schedule_two)
        self.subject_identifier = "111111"
        SubjectConsent.objects.create(subject_identifier=self.subject_identifier)

    def test_onschedule_updates_history(self):
        """Asserts returns the correct instances for the schedule.
        """
        for onschedule_model, schedule_name in [
            ("edc_visit_schedule.onscheduletwo", "schedule_two"),
            ("edc_visit_schedule.onschedulefour", "schedule_four"),
        ]:
            with self.subTest(
                onschedule_model=onschedule_model, schedule_name=schedule_name
            ):
                visit_schedule, schedule = site_visit_schedules.get_by_onschedule_model(
                    onschedule_model
                )
                subject_schedule = SubjectSchedule(
                    visit_schedule=visit_schedule, schedule=schedule
                )
                subject_schedule.put_on_schedule(
                    subject_identifier=self.subject_identifier,
                    onschedule_datetime=get_utcnow(),
                )
                try:
                    SubjectScheduleHistory.objects.get(
                        subject_identifier=self.subject_identifier,
                        schedule_name=schedule_name,
                    )
                except ObjectDoesNotExist:
                    self.fail("ObjectDoesNotExist unexpectedly raised")

    def test_multpile_consents(self):
        """Asserts does not raise if more than one consent
        for this subject
        """
        subject_identifier = "ABCDEF"
        SubjectConsent.objects.create(
            subject_identifier=subject_identifier, version="1"
        )
        SubjectConsent.objects.create(
            subject_identifier=subject_identifier, version="2"
        )
        visit_schedule, schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_visit_schedule.onscheduletwo"
        )
        subject_schedule = SubjectSchedule(
            visit_schedule=visit_schedule, schedule=schedule
        )
        try:
            subject_schedule.put_on_schedule(
                subject_identifier=subject_identifier, onschedule_datetime=get_utcnow()
            )
        except SubjectScheduleError:
            self.fail("SubjectScheduleError unexpectedly raised.")

    def test_resave(self):
        """Asserts returns the correct instances for the schedule.
        """
        visit_schedule, schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_visit_schedule.onscheduletwo"
        )
        subject_schedule = SubjectSchedule(
            visit_schedule=visit_schedule, schedule=schedule
        )
        subject_schedule.put_on_schedule(
            subject_identifier=self.subject_identifier, onschedule_datetime=get_utcnow()
        )
        subject_schedule.resave(subject_identifier=self.subject_identifier)

    def test_put_on_schedule(self):
        _, schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_visit_schedule.onschedule"
        )
        self.assertRaises(
            ObjectDoesNotExist,
            OnSchedule.objects.get,
            subject_identifier=self.subject_identifier,
        )
        schedule.put_on_schedule(
            subject_identifier=self.subject_identifier, onschedule_datetime=get_utcnow()
        )
        try:
            OnSchedule.objects.get(subject_identifier=self.subject_identifier)
        except ObjectDoesNotExist:
            self.fail("ObjectDoesNotExist unexpectedly raised")

    def test_take_off_schedule(self):
        visit_schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name="visit_schedule"
        )
        schedule = visit_schedule.schedules.get("schedule")
        schedule.put_on_schedule(subject_identifier=self.subject_identifier)
        schedule.take_off_schedule(
            subject_identifier=self.subject_identifier,
            offschedule_datetime=get_utcnow(),
        )
        try:
            OffSchedule.objects.get(subject_identifier=self.subject_identifier)
        except ObjectDoesNotExist:
            self.fail("ObjectDoesNotExist unexpectedly raised")
