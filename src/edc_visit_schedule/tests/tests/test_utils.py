from datetime import date

from dateutil.relativedelta import relativedelta
from django.test import TestCase, override_settings
from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_consent.consent import Consent
from edc_constants.constants import FEMALE, MALE
from edc_facility.import_holidays import import_holidays
from edc_protocol import Protocol
from edc_reference import site_reference_configs
from edc_sites.tests import SiteTestCaseMixin
from edc_utils import get_utcnow
from edc_visit_tracking.constants import SCHEDULED

from edc_visit_schedule.baseline import VisitScheduleBaselineError
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_schedule.utils import is_baseline
from edc_visit_schedule.visit import Visit
from edc_visit_schedule.visit_schedule import VisitSchedule
from visit_schedule_app.models import SubjectConsent, SubjectVisit


@override_settings(
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=get_utcnow() - relativedelta(years=5),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=get_utcnow() + relativedelta(years=1),
)
class TestVisitSchedule4(SiteTestCaseMixin, TestCase):
    def setUp(self):
        v1_consent = Consent(
            "visit_schedule_app.subjectconsent",
            version="1",
            start=Protocol().study_open_datetime,
            end=Protocol().study_close_datetime,
            age_min=18,
            age_is_adult=18,
            age_max=64,
            gender=[MALE, FEMALE],
        )

        import_holidays()
        site_consents.registry = {}
        site_consents.register(v1_consent)
        self.visit_schedule = VisitSchedule(
            name="visit_schedule",
            verbose_name="Visit Schedule",
            offstudy_model="visit_schedule_app.subjectoffstudy",
            death_report_model="visit_schedule_app.deathreport",
        )

        self.schedule = Schedule(
            name="schedule",
            onschedule_model="visit_schedule_app.onschedule",
            offschedule_model="visit_schedule_app.offschedule",
            appointment_model="edc_appointment.appointment",
            consent_model="visit_schedule_app.subjectconsent",
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

        site_reference_configs.registry = {}
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "visit_schedule_app.subjectvisit"}
        )

        self.subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345",
            consent_datetime=get_utcnow() - relativedelta(seconds=1),
            dob=date(1995, 1, 1),
            identity="11111",
            confirm_identity="11111",
        )
        self.subject_identifier = self.subject_consent.subject_identifier
        onschedule_datetime = get_utcnow() - relativedelta(years=4)
        _, schedule = site_visit_schedules.get_by_onschedule_model(
            "visit_schedule_app.onschedule"
        )
        schedule.put_on_schedule(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=onschedule_datetime,
        )
        self.appointments = Appointment.objects.all()

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
                timepoint=100,
                visit_schedule_name=subject_visit_0.visit_schedule_name,
                schedule_name=subject_visit_0.schedule_name,
                visit_code_sequence=0,
            )
        self.assertIn("Unknown timepoint", str(cm.exception))
