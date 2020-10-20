from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag
from edc_action_item import site_action_items
from edc_action_item.models import ActionItem
from edc_adverse_event.constants import DEATH_REPORT_ACTION
from edc_appointment.tests.appointment_test_case_mixin import AppointmentTestCaseMixin
from edc_list_data import load_list_data
from edc_metadata.tests.visit_schedule import visit_schedule
from edc_consent import site_consents
from edc_constants.constants import (
    ALIVE,
    CLOSED,
    HOSPITALIZED,
    NEW,
    OTHER,
    YES,
)
from edc_facility.import_holidays import import_holidays
from edc_ltfu.action_items import LossToFollowupAction
from edc_ltfu.constants import LOSS_TO_FOLLOWUP_ACTION
from edc_offstudy.action_items import EndOfStudyAction as BaseEndOfStudyAction
from edc_prn.constants import UNBLINDING_REVIEW_ACTION
from edc_utils import get_utcnow, get_dob
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.action_items import VisitMissedAction
from edc_visit_tracking.constants import MISSED_VISIT, SCHEDULED
from edc_metadata.tests.models import (
    SubjectConsent,
    SubjectVisit,
    SubjectVisitMissed,
    SubjectVisitMissedReasons,
)
from edc_reference import site_reference_configs

from .consents import v1_consent
from .models import LossToFollowup

list_data = {
    "edc_metadata.subjectvisitmissedreasons": [
        ("forgot", "Forgot / Can’t remember being told about appointment"),
        ("family_emergency", "Family emergency (e.g. funeral) and was away"),
        ("travelling", "Away travelling/visiting"),
        ("working_schooling", "Away working/schooling"),
        ("too_sick", "Too sick or weak to come to the centre"),
        ("lack_of_transport", "Transportation difficulty"),
        (HOSPITALIZED, "Hospitalized"),
        (OTHER, "Other reason (specify below)"),
    ],
}


class TestLossToFollowup(AppointmentTestCaseMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        site_consents.register(v1_consent)
        import_holidays()
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        load_list_data(
            list_data=list_data, model_name="edc_metadata.subjectvisitmissedreasons"
        )
        site_action_items.registry = {}

        class TestLossToFollowupAction(LossToFollowupAction):
            reference_model = "edc_ltfu.losstofollowup"
            admin_site_name = "edc_ltfu_admin"

        class SubjectVisitMissedAction(VisitMissedAction):
            reference_model = "edc_metadata.subjectvisitmissed"
            admin_site_name = "edc_ltfu_admin"

        class EndOfStudyAction(BaseEndOfStudyAction):
            reference_model = "edc_ltfu.offschedule"
            admin_site_name = "edc_ltfu_admin"
            parent_action_names = [
                UNBLINDING_REVIEW_ACTION,
                DEATH_REPORT_ACTION,
                LOSS_TO_FOLLOWUP_ACTION,
            ]

        site_action_items.register(TestLossToFollowupAction)
        site_action_items.register(SubjectVisitMissedAction)
        site_action_items.register(EndOfStudyAction)

        self.visit_schedule_name = "visit_schedule1"
        self.schedule_name = "schedule1"

        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)

        self.schedule = visit_schedule.schedules.get("schedule")

        site_reference_configs.registry = {}
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "edc_metadata.subjectvisit"}
        )

        self.subject_identifier = "111111111"
        self.subject_identifiers = [
            self.subject_identifier,
            "222222222",
            "333333333",
            "444444444",
        ]
        self.consent_datetime = get_utcnow() - relativedelta(weeks=4)
        dob = get_dob(age_in_years=25, now=self.consent_datetime)
        for subject_identifier in self.subject_identifiers:
            subject_consent = SubjectConsent.objects.create(
                subject_identifier=subject_identifier,
                identity=subject_identifier,
                confirm_identity=subject_identifier,
                consent_datetime=self.consent_datetime,
                dob=dob,
            )
            self.schedule.put_on_schedule(
                subject_identifier=subject_consent.subject_identifier,
                onschedule_datetime=self.consent_datetime,
            )
        self.subject_consent = SubjectConsent.objects.get(
            subject_identifier=self.subject_identifier, dob=dob
        )

    def test_ltfu_creates_and_closes_action(self):
        LossToFollowup.objects.create(
            subject_identifier=self.subject_identifier,
            last_seen_datetime=get_utcnow(),
            phone_attempts=3,
            home_visited=YES,
            loss_category="lost",
        )
        try:
            ActionItem.objects.get(
                subject_identifier=self.subject_identifier,
                action_type__name=LOSS_TO_FOLLOWUP_ACTION,
                status=CLOSED,
            )
        except ObjectDoesNotExist:
            self.fail("ObjectDoesNotExist unexpectedly raised")

    def test_missed_visit_creates_new_ltfu_action(self):
        appointment = self.get_appointment(
            subject_identifier=self.subject_identifier,
            visit_code="1000",
            visit_code_sequence=0,
            reason=SCHEDULED,
            appt_datetime=get_utcnow(),
        )

        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
            reason=MISSED_VISIT,
        )

        obj = SubjectVisitMissed.objects.create(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            survival_status=ALIVE,
            contact_attempted=YES,
            contact_attempts_count=1,
            contact_made=YES,
            contact_last_date=get_utcnow(),
            ltfu=YES,
        )
        obj.missed_reasons.add(SubjectVisitMissedReasons.objects.get(name=HOSPITALIZED))
        try:
            ActionItem.objects.get(
                subject_identifier=self.subject_identifier,
                action_type__name=LOSS_TO_FOLLOWUP_ACTION,
                status=NEW,
            )
        except ObjectDoesNotExist:
            self.fail("ObjectDoesNotExist unexpectedly raised")
