from datetime import date
from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag
from edc_appointment.models import Appointment
from edc_sites.tests import SiteTestCaseMixin
from edc_utils import get_utcnow
from edc_facility.import_holidays import import_holidays
from edc_registration.models import RegisteredSubject

from ..constants import ON_SCHEDULE
from ..models import SubjectScheduleHistory
from ..schedule import Schedule
from ..site_visit_schedules import site_visit_schedules, SiteVisitScheduleError
from ..subject_schedule import NotOnScheduleError, InvalidOffscheduleDate
from ..subject_schedule import NotConsentedError, UnknownSubjectError
from ..visit import Visit, Crf, FormsCollectionError, FormsCollection
from ..visit_schedule import VisitSchedule
from ..visit_schedule import VisitScheduleNameError, AlreadyRegisteredSchedule
from .models import OnSchedule, OnScheduleThree, OffSchedule
from .models import SubjectVisit, SubjectConsent


class TestVisitSchedule(SiteTestCaseMixin, TestCase):
    def setUp(self):
        super().setUp()
        import_holidays()

    def test_visit_schedule_name(self):
        """Asserts raises on invalid name.
        """
        self.assertRaises(
            VisitScheduleNameError,
            VisitSchedule,
            name="visit &&&& schedule",
            verbose_name="Visit Schedule",
            offstudy_model="edc_visit_schedule.deathreport",
            death_report_model="edc_visit_schedule.deathreport",
        )

    def test_visit_schedule_repr(self):
        """Asserts repr evaluates correctly.
        """
        v = VisitSchedule(
            name="visit_schedule",
            verbose_name="Visit Schedule",
            offstudy_model="edc_visit_schedule.deathreport",
            death_report_model="edc_visit_schedule.deathreport",
        )
        self.assertTrue(v.__repr__())

    def test_visit_schedule_validates(self):
        visit_schedule = VisitSchedule(
            name="visit_schedule",
            verbose_name="Visit Schedule",
            offstudy_model="edc_visit_schedule.subjectoffstudy",
            death_report_model="edc_visit_schedule.deathreport",
        )
        errors = visit_schedule.check()
        if errors:
            self.fail(f"visit_schedule.check() unexpectedly failed")


class TestVisitSchedule2(SiteTestCaseMixin, TestCase):
    def setUp(self):
        import_holidays()
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

        self.schedule2 = Schedule(
            name="schedule_two",
            onschedule_model="edc_visit_schedule.onscheduletwo",
            offschedule_model="edc_visit_schedule.offscheduletwo",
            appointment_model="edc_appointment.appointment",
            consent_model="edc_visit_schedule.subjectconsent",
        )

        self.schedule3 = Schedule(
            name="schedule_three",
            onschedule_model="edc_visit_schedule.onschedulethree",
            offschedule_model="edc_visit_schedule.offschedulethree",
            appointment_model="edc_appointment.appointment",
            consent_model="edc_visit_schedule.subjectconsent",
        )

    def test_visit_schedule_add_schedule(self):
        try:
            self.visit_schedule.add_schedule(self.schedule)
        except AlreadyRegisteredSchedule:
            self.fail("AlreadyRegisteredSchedule unexpectedly raised.")

    def test_visit_schedule_add_schedule_invalid_appointment_model(self):
        self.assertRaises(
            AttributeError,
            Schedule,
            name="schedule_bad",
            onschedule_model="edc_visit_schedule.onschedule",
            offschedule_model="edc_visit_schedule.offschedule",
            appointment_model=None,
            consent_model="edc_visit_schedule.subjectconsent",
        )

    def test_visit_schedule_add_schedule_with_appointment_model(self):
        self.visit_schedule.add_schedule(self.schedule3)
        for schedule in self.visit_schedule.schedules.values():
            self.assertEqual(schedule.appointment_model, "edc_appointment.appointment")

    def test_visit_already_added_to_schedule(self):
        self.visit_schedule.add_schedule(self.schedule)
        self.assertRaises(
            AlreadyRegisteredSchedule, self.visit_schedule.add_schedule, self.schedule
        )

    def test_visit_schedule_get_schedules(self):
        self.visit_schedule.add_schedule(self.schedule)
        self.assertIn(self.schedule, self.visit_schedule.schedules.values())
        self.visit_schedule.add_schedule(self.schedule3)
        self.assertIn(self.schedule3, self.visit_schedule.schedules.values())

    def test_crfs_unique_show_order(self):
        self.assertRaises(
            FormsCollectionError,
            FormsCollection,
            Crf(show_order=10, model="edc_example.CrfOne"),
            Crf(show_order=20, model="edc_example.CrfTwo"),
            Crf(show_order=20, model="edc_example.CrfThree"),
        )


class TestVisitSchedule3(SiteTestCaseMixin, TestCase):
    def setUp(self):
        import_holidays()
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

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            timepoint=1,
        )
        self.schedule.add_visit(visit)
        self.visit_schedule.add_schedule(self.schedule)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(self.visit_schedule)
        self.subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345",
            consent_datetime=get_utcnow() - relativedelta(seconds=1),
            dob=date(1995, 1, 1),
            identity="11111",
            confirm_identity="11111",
        )
        self.subject_identifier = self.subject_consent.subject_identifier

    def test_put_on_schedule_creates_history(self):
        self.schedule.put_on_schedule(
            subject_identifier=self.subject_identifier, onschedule_datetime=get_utcnow()
        )
        self.assertEqual(
            SubjectScheduleHistory.objects.filter(
                subject_identifier=self.subject_identifier
            ).count(),
            1,
        )

    def test_onschedule_creates_history(self):
        onschedule_model_obj = OnSchedule.objects.create(
            subject_identifier=self.subject_identifier, onschedule_datetime=get_utcnow()
        )
        self.assertEqual(
            SubjectScheduleHistory.objects.filter(
                subject_identifier=self.subject_identifier
            ).count(),
            1,
        )
        history_obj = SubjectScheduleHistory.objects.get(
            subject_identifier=self.subject_identifier
        )
        self.assertIsNone(history_obj.__dict__.get("offschedule_datetime"))
        self.assertEqual(
            history_obj.__dict__.get("onschedule_datetime"),
            onschedule_model_obj.onschedule_datetime,
        )
        self.assertEqual(history_obj.__dict__.get("schedule_status"), ON_SCHEDULE)

    def test_can_create_offschedule_with_onschedule(self):
        # signal puts on schedule
        OnSchedule.objects.create(
            subject_identifier=self.subject_identifier, onschedule_datetime=get_utcnow()
        )
        try:
            OffSchedule.objects.create(
                subject_identifier=self.subject_identifier,
                offschedule_datetime=get_utcnow(),
            )
        except Exception as e:
            self.fail(f"Exception unexpectedly raised. Got {e}.")

    def test_creates_appointments(self):
        # signal puts on schedule
        OnSchedule.objects.create(
            subject_identifier=self.subject_identifier, onschedule_datetime=get_utcnow()
        )
        self.assertGreater(Appointment.objects.all().count(), 0)

    def test_creates_appointments_starting_with_onschedule_datetime(self):
        _, schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_visit_schedule.onschedule"
        )
        onschedule_datetime = get_utcnow() - relativedelta(months=1)
        schedule.put_on_schedule(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=onschedule_datetime,
        )
        appointment = Appointment.objects.all().order_by("appt_datetime").first()
        self.assertEqual(appointment.appt_datetime, onschedule_datetime)

    def test_cannot_create_offschedule_without_onschedule(self):
        self.assertEqual(
            OnSchedule.objects.filter(
                subject_identifier=self.subject_identifier
            ).count(),
            0,
        )
        self.assertRaises(
            NotOnScheduleError,
            OffSchedule.objects.create,
            subject_identifier=self.subject_identifier,
        )

    def test_cannot_create_offschedule_before_onschedule(self):
        OnSchedule.objects.create(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=get_utcnow() - relativedelta(months=1),
        )
        self.assertRaises(
            InvalidOffscheduleDate,
            OffSchedule.objects.create,
            subject_identifier=self.subject_identifier,
            offschedule_datetime=get_utcnow() - relativedelta(months=2),
        )

    def test_cannot_create_offschedule_before_last_visit(self):
        _, schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_visit_schedule.onschedule"
        )
        schedule.put_on_schedule(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=get_utcnow() - relativedelta(months=1),
        )
        appointments = Appointment.objects.all()
        SubjectVisit.objects.create(
            appointment=appointments[0],
            subject_identifier=self.subject_identifier,
            report_datetime=appointments[0].appt_datetime,
        )
        self.assertRaises(
            InvalidOffscheduleDate,
            schedule.take_off_schedule,
            subject_identifier=self.subject_identifier,
            offschedule_datetime=appointments[0].appt_datetime - relativedelta(days=1),
        )

    def test_cannot_put_on_schedule_if_visit_schedule_not_registered_subject(self):
        _, schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_visit_schedule.onschedule"
        )
        RegisteredSubject.objects.all().delete()
        self.assertRaises(
            UnknownSubjectError,
            schedule.put_on_schedule,
            subject_identifier=self.subject_identifier,
            onschedule_datetime=get_utcnow(),
        )

    def test_cannot_put_on_schedule_if_visit_schedule_not_consented(self):
        _, schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_visit_schedule.onschedule"
        )
        SubjectConsent.objects.all().delete()
        self.assertRaises(
            NotConsentedError,
            schedule.put_on_schedule,
            subject_identifier=self.subject_identifier,
            onschedule_datetime=get_utcnow(),
        )

    def test_cannot_put_on_schedule_if_schedule_not_added(self):
        self.assertRaises(SiteVisitScheduleError, OnScheduleThree.objects.create)
