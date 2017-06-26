from collections import OrderedDict
from django.test import TestCase, tag
from faker import Faker

from edc_constants.constants import MALE, FEMALE
from edc_registration.models import RegisteredSubject
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from ..constants import NOT_REQUIRED, REQUIRED
from ..models import CrfMetadata
from ..rules import RuleGroup, CrfRule, Logic, P, site_metadata_rules
from .models import Appointment, SubjectVisit, Enrollment
from .visit_schedule import visit_schedule

fake = Faker()


class CrfRuleGroupGender(RuleGroup):

    crfs_male = CrfRule(
        logic=Logic(
            predicate=P('gender', 'eq', MALE),
            consequence=REQUIRED,
            alternative=NOT_REQUIRED),
        target_models=['crffour', 'crffive'])

    crfs_female = CrfRule(
        logic=Logic(
            predicate=P('gender', 'eq', FEMALE),
            consequence=REQUIRED,
            alternative=NOT_REQUIRED),
        target_models=['crftwo', 'crfthree'])

    class Meta:
        app_label = 'edc_metadata'


class TestMetadataRulesWithGender(TestCase):

    def setUp(self):

        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)

        # note crfs in visit schedule are all set to REQUIRED by default.
        self.schedule = site_visit_schedules.get_schedule(
            visit_schedule_name='visit_schedule',
            schedule_name='schedule')

        site_metadata_rules.registry = OrderedDict()
        site_metadata_rules.register(rule_group_cls=CrfRuleGroupGender)

    def enroll(self, gender=None):
        subject_identifier = fake.credit_card_number()
        self.registered_subject = RegisteredSubject.objects.create(
            subject_identifier=subject_identifier, gender=gender)
        Enrollment.objects.create(subject_identifier=subject_identifier)
        self.appointment = Appointment.objects.get(
            subject_identifier=subject_identifier,
            visit_code=self.schedule.visits.first.code)
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED,
            subject_identifier=subject_identifier)
        return subject_visit

    def test_example_rules_run_female_required(self):
        subject_visit = self.enroll(gender=FEMALE)
        for target_model in ['edc_metadata.crftwo', 'edc_metadata.crfthree']:
            with self.subTest(target_model=target_model):
                obj = CrfMetadata.objects.get(
                    model=target_model,
                    subject_identifier=subject_visit.subject_identifier,
                    visit_code=subject_visit.visit_code)
                self.assertEqual(obj.entry_status, REQUIRED)

    def test_example_rules_run_female_not_required(self):
        subject_visit = self.enroll(gender=FEMALE)
        for target_model in ['edc_metadata.crffour', 'edc_metadata.crffive']:
            with self.subTest(target_model=target_model):
                obj = CrfMetadata.objects.get(
                    model=target_model,
                    subject_identifier=subject_visit.subject_identifier,
                    visit_code=subject_visit.visit_code)
                self.assertEqual(obj.entry_status, NOT_REQUIRED)

    def test_example_rules_run_male_not_required(self):
        subject_visit = self.enroll(gender=MALE)
        for target_model in ['edc_metadata.crftwo', 'edc_metadata.crfthree']:
            with self.subTest(target_model=target_model):
                obj = CrfMetadata.objects.get(
                    model=target_model,
                    subject_identifier=subject_visit.subject_identifier,
                    visit_code=subject_visit.visit_code)
                self.assertEqual(obj.entry_status, NOT_REQUIRED)

    def test_example_rules_run_male_required(self):
        subject_visit = self.enroll(gender=MALE)
        for target_model in ['edc_metadata.crffour', 'edc_metadata.crffive']:
            with self.subTest(target_model=target_model):
                obj = CrfMetadata.objects.get(
                    model=target_model,
                    subject_identifier=subject_visit.subject_identifier,
                    visit_code=subject_visit.visit_code)
                self.assertEqual(obj.entry_status, REQUIRED)
