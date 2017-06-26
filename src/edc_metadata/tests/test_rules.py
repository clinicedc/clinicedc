from dateutil.relativedelta import relativedelta

from django.apps import apps as django_apps
from django.test import TestCase, tag
# from model_mommy import mommy

from edc_base.utils import get_utcnow
from edc_constants.constants import MALE, FEMALE
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ..constants import NOT_REQUIRED, REQUIRED, KEYED
from ..models import CrfMetadata

from ..rules.crf_rule import CrfRule
from ..rules.exceptions import RuleError
from ..rules.logic import Logic
from ..rules.predicate import P, PF
from ..rules.rule_group import RuleGroup
from ..rules.site_metadata_rules import site_metadata_rules, MetadataRulesAlreadyRegistered
from .models import CrfOne, CrfTwo, CrfThree, CrfFive, CrfFour, Enrollment
from .models import Appointment, SubjectVisit, SubjectConsent
from edc_registration.models import RegisteredSubject
from edc_metadata.tests.visit_schedule import visit_schedule
from edc_visit_tracking.constants import SCHEDULED
from edc_metadata.tests.metadata_rules import CrfRuleGroup
from collections import OrderedDict

edc_registration_app_config = django_apps.get_app_config('edc_registration')


class MetadataRulesTests(TestCase):

    def test_logic(self):
        logic = Logic(
            predicate=lambda x: True if x else False,
            consequence=REQUIRED,
            alternative=NOT_REQUIRED)
        self.assertTrue(logic.predicate(1) is True)
        self.assertTrue(logic.consequence == REQUIRED)
        self.assertTrue(logic.alternative == NOT_REQUIRED)

    def test_logic3(self):
        self.assertRaises(
            RuleError, Logic,
            predicate=lambda x: False if x else True,
            consequence='OLD',
            alternative=NOT_REQUIRED)


class MetadataRulesTestsMale(TestCase):

    def setUp(self):
        site_metadata_rules.registry = OrderedDict()
        site_metadata_rules.register(rule_group=CrfRuleGroup)
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)
        self.schedule = site_visit_schedules.get_schedule(
            visit_schedule_name='visit_schedule',
            schedule_name='schedule')
        self.subject_identifier = '1111111'
        self.registered_subject = RegisteredSubject.objects.create(
            subject_identifier=self.subject_identifier, gender=None)
        self.enrollment = Enrollment.objects.create(
            subject_identifier=self.subject_identifier)
        self.appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code=self.schedule.visits.first.code)

    def enroll(self, subject_identifier=None, gender=None):
        subject_identifier = subject_identifier or self.subject_identifier
        gender = gender or MALE
        self.registered_subject = RegisteredSubject.objects.create(
            subject_identifier=subject_identifier, gender=gender)
        Enrollment.objects.create(subject_identifier=subject_identifier)
        self.appointment = Appointment.objects.get(
            subject_identifier=subject_identifier,
            visit_code=self.schedule.visits.first.code)
        SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED)

    @tag('1')
    def test_example_rules_run_if_male(self):
        """Assert CrfFour, CrfFive is required for males only and
        CrfTwo, CrfThree required for females only.
        """

        for index, gender in enumerate([MALE, FEMALE]):
            with self.subTest(gender=gender, index=index):
                subject_identifier = f'12345{index}'
                self.enroll(
                    subject_identifier=subject_identifier,
                    gender=gender)
                self.assertEqual(
                    CrfMetadata.objects.get(
                        model=CrfTwo._meta.label_lower,
                        subject_identifier=subject_identifier,
                        visit_code=self.schedule.visits.first.code
                    ).entry_status, REQUIRED if gender == FEMALE else NOT_REQUIRED)
                self.assertEqual(
                    CrfMetadata.objects.get(
                        model=CrfThree._meta.label_lower,
                        subject_identifier=subject_identifier,
                        visit_code=self.schedule.visits.first.code
                    ).entry_status, REQUIRED if gender == FEMALE else NOT_REQUIRED)
                self.assertEqual(
                    CrfMetadata.objects.get(
                        model=CrfFour._meta.label_lower,
                        subject_identifier=subject_identifier,
                        visit_code=self.schedule.visits.first.code
                    ).entry_status, REQUIRED if gender == MALE else NOT_REQUIRED)
                self.assertEqual(
                    CrfMetadata.objects.get(
                        model=CrfFive._meta.label_lower,
                        subject_identifier=subject_identifier,
                        visit_code=self.schedule.visits.first.code
                    ).entry_status, REQUIRED if gender == MALE else NOT_REQUIRED)

    @tag('1')
    def test_register_twice_raises(self):

        class TestCrfRuleGroup(RuleGroup):

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

        site_metadata_rules.register(rule_group=TestCrfRuleGroup)
        self.assertRaises(
            MetadataRulesAlreadyRegistered,
            site_metadata_rules.register, TestCrfRuleGroup)

    def test_example2(self):
        """Asserts CrfTwo is REQUIRED if f1==\'car\' as specified
        by edc_example.rule_groups.ExampleRuleGroup2."""
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfTwo._meta.label_lower).entry_status, NOT_REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfThree._meta.label_lower).entry_status, NOT_REQUIRED)
        CrfOne.objects.create(subject_visit=self.subject_visit, f1='car')
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfTwo._meta.label_lower).entry_status, REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfThree._meta.label_lower).entry_status, NOT_REQUIRED)

    def test_example3(self):
        """Asserts CrfThree is REQUIRED if f1==\'bicycle\' as specified
        by edc_example.rule_groups.ExampleRuleGroup2."""
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfTwo._meta.label_lower).entry_status, NOT_REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfThree._meta.label_lower).entry_status, NOT_REQUIRED)
        CrfOne.objects.create(subject_visit=self.subject_visit, f1='bicycle')
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfTwo._meta.label_lower).entry_status, NOT_REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfThree._meta.label_lower).entry_status, REQUIRED)

    def test_example4(self):
        """Asserts CrfThree is REQUIRED if f1==\'bicycle\' but then not when f1 is changed to \'car\' as specified
        by edc_example.rule_groups.ExampleRuleGroup2."""
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfTwo._meta.label_lower).entry_status, NOT_REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfThree._meta.label_lower).entry_status, NOT_REQUIRED)
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit, f1='bicycle')
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfTwo._meta.label_lower).entry_status, NOT_REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfThree._meta.label_lower).entry_status, REQUIRED)
        crf_one.f1 = 'car'
        crf_one.save()
        self.assertEqual(
            CrfMetadata.objects.get(
                model=CrfTwo._meta.label_lower,
                subject_identifier=self.subject_visit.subject_identifier,
                visit_code=self.schedule.visits.first.code
            ).entry_status, REQUIRED)
        self.assertEqual(
            CrfMetadata.objects.get(
                model=CrfThree._meta.label_lower,
                subject_identifier=self.subject_visit.subject_identifier,
                visit_code=self.schedule.visits.first.code
            ).entry_status, NOT_REQUIRED)

    def test_example5(self):
        """Asserts same as above for edc_example.rule_groups.ExampleRuleGroup2 but add
        a second visit and CrfOne."""
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfTwo._meta.label_lower).entry_status, NOT_REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfThree._meta.label_lower).entry_status, NOT_REQUIRED)
        CrfOne.objects.create(subject_visit=self.subject_visit, f1='bicycle')
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfTwo._meta.label_lower).entry_status, NOT_REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfThree._meta.label_lower).entry_status, REQUIRED)
        next_visit = self.schedule.get_next_visit(
            self.schedule.visits.first.code)
        appointment = Appointment.objects.get(
            subject_identifier=self.enrollment.subject_identifier,
            visit_code=next_visit.code)
        subject_visit2 = mommy.make_recipe(
            'edc_example.subjectvisit', appointment=appointment)
        CrfOne.objects.create(subject_visit=subject_visit2, f1='car')
        self.assertEqual(
            CrfMetadata.objects.get(
                model=CrfTwo._meta.label_lower,
                subject_identifier=self.subject_visit.subject_identifier,
                visit_code=self.schedule.visits.first.code
            ).entry_status, NOT_REQUIRED)
        self.assertEqual(
            CrfMetadata.objects.get(
                model=CrfThree._meta.label_lower,
                subject_identifier=self.subject_visit1.subject_identifier,
                visit_code=self.schedule.visits.first.code
            ).entry_status, REQUIRED)
        self.assertEqual(
            CrfMetadata.objects.get(
                model=CrfTwo._meta.label_lower,
                subject_identifier=subject_visit2.subject_identifier,
                visit_code=next_visit.code
            ).entry_status, REQUIRED)
        self.assertEqual(
            CrfMetadata.objects.get(
                model=CrfThree._meta.label_lower,
                subject_identifier=subject_visit2.subject_identifier,
                visit_code=next_visit.code
            ).entry_status, NOT_REQUIRED)

    def test_example6(self):
        """Asserts resaving subject visit does not overwrite."""
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfTwo._meta.label_lower).entry_status, NOT_REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfThree._meta.label_lower).entry_status, NOT_REQUIRED)
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit, f1='bicycle')
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfTwo._meta.label_lower).entry_status, NOT_REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfThree._meta.label_lower).entry_status, REQUIRED)
        self.subject_visit.save()
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfTwo._meta.label_lower).entry_status, NOT_REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfThree._meta.label_lower).entry_status, REQUIRED)

    def test_example7(self):
        """Asserts if instance exists, rule is ignored."""
        self.enroll(subject_identifier, gender)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfTwo._meta.label_lower).entry_status, NOT_REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfThree._meta.label_lower).entry_status, NOT_REQUIRED)
        crf_one = CrfOne.objects.create(
            subject_visit=subject_visit, f1='bicycle')
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfTwo._meta.label_lower).entry_status, NOT_REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfThree._meta.label_lower).entry_status, REQUIRED)
        CrfThree.objects.create(subject_visit=subject_visit)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfTwo._meta.label_lower).entry_status, NOT_REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfThree._meta.label_lower).entry_status, KEYED)
        crf_one.f1 = 'car'
        crf_one.save()
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfTwo._meta.label_lower).entry_status, REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfThree._meta.label_lower).entry_status, KEYED)
        crf_one.f1 = 'bicycle'
        crf_one.save()
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfTwo._meta.label_lower).entry_status, NOT_REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfThree._meta.label_lower).entry_status, KEYED)

    @tag('1')
    def test_delete(self):
        """Asserts delete returns to default entry status."""
        self.enroll(subject_identifier='12345678')
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfTwo._meta.label_lower).entry_status, NOT_REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfThree._meta.label_lower).entry_status, NOT_REQUIRED)
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit, f1='bicycle')
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfTwo._meta.label_lower).entry_status, NOT_REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfThree._meta.label_lower).entry_status, REQUIRED)
        crf_one.delete()
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfTwo._meta.label_lower).entry_status, NOT_REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfThree._meta.label_lower).entry_status, NOT_REQUIRED)
