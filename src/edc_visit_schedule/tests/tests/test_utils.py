from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.sites import all_sites
from dateutil.relativedelta import relativedelta
from django.test import TestCase, override_settings, tag

from edc_appointment.models import Appointment
from edc_consent.site_consents import site_consents
from edc_facility.import_holidays import import_holidays
from edc_sites.site import sites as site_sites
from edc_sites.tests import SiteTestCaseMixin
from edc_sites.utils import add_or_update_django_sites
from edc_visit_schedule.baseline import VisitScheduleBaselineError
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_schedule.utils import get_duplicates, is_baseline
from edc_visit_schedule.visit import Visit
from edc_visit_schedule.visit_schedule import VisitSchedule
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit


@tag("visit_schedule")
@time_machine.travel(datetime(2025, 4, 1, 8, 00, tzinfo=ZoneInfo("UTC")))
@override_settings(SITE_ID=10)
class TestVisitSchedule4(SiteTestCaseMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

    def setUp(self):
        site_consents.registry = {}
        site_consents.register(consent_v1)
        self.visit_schedule = VisitSchedule(
            name="visit_schedule",
            verbose_name="Visit Schedule",
            offstudy_model="edc_offstudy.subjectoffstudy",
            death_report_model="clinicedc_tests.deathreport",
        )

        self.schedule = Schedule(
            name="schedule",
            onschedule_model="edc_visit_schedule.onschedule",
            offschedule_model="edc_visit_schedule.offschedule",
            appointment_model="edc_appointment.appointment",
            consent_definitions=[consent_v1],
            base_timepoint=1,
        )

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            timepoint=1,
        )
        self.schedule.add_visit(visit)
        visit = Visit(
            code="1010",
            rbase=relativedelta(days=28),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            timepoint=2,
        )
        self.schedule.add_visit(visit)

        self.visit_schedule.add_schedule(self.schedule)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(self.visit_schedule)

        helper = Helper()
        consent = helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule", schedule_name="schedule"
        )
        self.subject_identifier = consent.subject_identifier
        self.appointments = Appointment.objects.filter(
            subject_identifier=self.subject_identifier
        ).order_by("timepoint", "visit_code_sequence")

    def test_is_baseline_with_instance(self):
        subject_visit_0 = SubjectVisit.objects.create(
            appointment=self.appointments[0],
            subject_identifier=self.subject_identifier,
            report_datetime=self.appointments[0].appt_datetime,
            reason=SCHEDULED,
        )
        subject_visit_1 = SubjectVisit.objects.create(
            appointment=self.appointments[1],
            subject_identifier=self.subject_identifier,
            report_datetime=self.appointments[1].appt_datetime,
            reason=SCHEDULED,
        )

        self.assertTrue(is_baseline(instance=subject_visit_0))
        self.assertFalse(is_baseline(instance=subject_visit_1))

    def test_is_baseline_with_params(self):
        subject_visit_0 = SubjectVisit.objects.create(
            appointment=self.appointments[0],
            subject_identifier=self.subject_identifier,
            report_datetime=self.appointments[0].appt_datetime,
            reason=SCHEDULED,
        )
        subject_visit_1 = SubjectVisit.objects.create(
            appointment=self.appointments[1],
            subject_identifier=self.subject_identifier,
            report_datetime=self.appointments[1].appt_datetime,
            reason=SCHEDULED,
        )

        # call with no required params raises
        self.assertRaises(VisitScheduleBaselineError, is_baseline)

        # call with all required params but visit_code_sequence raises
        with self.assertRaises(VisitScheduleBaselineError) as cm:
            is_baseline(
                timepoint=subject_visit_0.appointment.timepoint,
                visit_schedule_name=subject_visit_0.appointment.visit_schedule_name,
                schedule_name=subject_visit_0.appointment.schedule_name,
            )
        self.assertIn("visit_code_sequence", str(cm.exception))

        self.assertTrue(
            is_baseline(
                timepoint=subject_visit_0.appointment.timepoint,
                visit_schedule_name=subject_visit_0.appointment.visit_schedule_name,
                schedule_name=subject_visit_0.appointment.schedule_name,
                visit_code_sequence=0,
            )
        )
        self.assertFalse(
            is_baseline(
                timepoint=subject_visit_0.timepoint,
                visit_schedule_name=subject_visit_0.visit_schedule_name,
                schedule_name=subject_visit_0.schedule_name,
                visit_code_sequence=1,
            )
        )
        self.assertFalse(
            is_baseline(
                timepoint=subject_visit_1.timepoint,
                visit_schedule_name=subject_visit_0.visit_schedule_name,
                schedule_name=subject_visit_0.schedule_name,
                visit_code_sequence=0,
            )
        )

        with self.assertRaises(VisitScheduleBaselineError) as cm:
            is_baseline(
                timepoint=Decimal("100.0"),
                visit_schedule_name=subject_visit_0.visit_schedule_name,
                schedule_name=subject_visit_0.schedule_name,
                visit_code_sequence=0,
            )
        self.assertIn("Unknown timepoint", str(cm.exception))

    def test_get_duplicates_returns_duplicates(self):
        self.assertListEqual(get_duplicates(["one", "one"]), ["one"])
        self.assertListEqual(get_duplicates(["one", "one", "two"]), ["one"])
        self.assertListEqual(get_duplicates(["one", "two", "two"]), ["two"])
        self.assertListEqual(get_duplicates(["one", "two", "two", "one"]), ["one", "two"])
        self.assertListEqual(
            get_duplicates(["one", "two", "three", "three", "two", "one"]),
            ["one", "two", "three"],
        )
        self.assertListEqual(
            get_duplicates(["three", "two", "one", "one", "two", "three"]),
            ["three", "two", "one"],
        )
        self.assertListEqual(get_duplicates([1, 1]), [1])
        self.assertListEqual(get_duplicates([1, 1, 2]), [1])
        self.assertListEqual(get_duplicates([1, 2, 2]), [2])
        self.assertListEqual(get_duplicates([1, 2, 2, 1]), [1, 2])
        self.assertListEqual(get_duplicates([1, 2, 2, 3, 1]), [1, 2])
        self.assertListEqual(get_duplicates([1, 2, 3, 3, 2, 1]), [1, 2, 3])
        self.assertListEqual(get_duplicates([3, 2, 1, 1, 2, 3]), [3, 2, 1])

    def test_get_duplicates_with_no_duplicates_returns_empty_list(self):
        self.assertListEqual(get_duplicates([]), [])

        self.assertListEqual(get_duplicates(["one"]), [])
        self.assertListEqual(get_duplicates(["one", "two", "three"]), [])

        self.assertListEqual(get_duplicates([1]), [])
        self.assertListEqual(get_duplicates([1, 2, 3]), [])
