from collections import OrderedDict
from django.test import TestCase, tag
from faker import Faker

from edc_constants.constants import MALE, FEMALE
from edc_registration.models import RegisteredSubject
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from ..constants import NOT_REQUIRED, REQUIRED
from ..models import CrfMetadata
from ..rules import RuleGroup, CrfRule, Logic, P, PF, site_metadata_rules
from ..rules import RuleEvaluatorRegisterSubjectError, RuleGroupModelConflict
from ..rules import TargetModelConflict, PredicateError, RuleEvaluatorError
from ..rules import TargetModelLookupError, TargetModelMissingManagerMethod
from ..rules import RuleGroupMetaError
from .models import Appointment, SubjectVisit, Enrollment, CrfOne
from .visit_schedule import visit_schedule
from pprint import pprint

fake = Faker()


class CrfRuleGroupWithSourceModel(RuleGroup):
    """Specifies source model.
    """

    crfs_male = CrfRule(
        logic=Logic(
            predicate=P('f1', 'eq', 'car'),
            consequence=REQUIRED,
            alternative=NOT_REQUIRED),
        target_models=['crffive', 'crffour'])

    crfs_female = CrfRule(
        logic=Logic(
            predicate=P('f1', 'eq', 'bicycle'),
            consequence=REQUIRED,
            alternative=NOT_REQUIRED),
        target_models=['crfthree', 'crftwo'])

    class Meta:
        app_label = 'edc_metadata'
        source_model = 'edc_metadata.crfone'


class CrfRuleGroupWithoutSourceModel(RuleGroup):

    crfs_male = CrfRule(
        logic=Logic(
            predicate=P('gender', 'eq', MALE),
            consequence=REQUIRED,
            alternative=NOT_REQUIRED),
        target_models=['crffive', 'crffour'])

    crfs_female = CrfRule(
        logic=Logic(
            predicate=P('gender', 'eq', FEMALE),
            consequence=REQUIRED,
            alternative=NOT_REQUIRED),
        target_models=['crfthree', 'crftwo'])

    class Meta:
        app_label = 'edc_metadata'


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

    def test_rules_with_source_model(self):
        for rule in CrfRuleGroupWithSourceModel._meta.options.get('rules'):
            self.assertEqual(rule.source_model, 'edc_metadata.crfone')

    def test_rules_without_source_model(self):
        for rule in CrfRuleGroupWithoutSourceModel._meta.options.get('rules'):
            self.assertIsNone(rule.source_model)

    def test_rules_run_source_object_is_none(self):
        subject_visit = self.enroll(MALE)
        for rule in CrfRuleGroupWithoutSourceModel._meta.options.get('rules'):
            with self.subTest(rule=rule):
                result = rule.run(subject_visit)
                if rule.name == 'crfs_male':
                    self.assertEqual(
                        result,
                        {'edc_metadata.crffive': REQUIRED,
                         'edc_metadata.crffour': REQUIRED})
                elif rule.name == 'crfs_female':
                    self.assertEqual(
                        result,
                        {'edc_metadata.crfthree': NOT_REQUIRED,
                         'edc_metadata.crftwo': NOT_REQUIRED})

    def test_rules_skipped_if_no_source(self):
        subject_visit = self.enroll(MALE)
        for rule in CrfRuleGroupWithSourceModel._meta.options.get('rules'):
            with self.subTest(rule=rule):
                result = rule.run(subject_visit)
                if rule.name == 'crfs_male':
                    self.assertEqual(
                        result,
                        {'edc_metadata.crffive': None,
                         'edc_metadata.crffour': None})
                elif rule.name == 'crfs_female':
                    self.assertEqual(
                        result,
                        {'edc_metadata.crfthree': None,
                         'edc_metadata.crftwo': None})

    def test_rules_run_if_source_f1_equals_car(self):
        subject_visit = self.enroll(MALE)
        CrfOne.objects.create(subject_visit=subject_visit, f1='car')
        for rule in CrfRuleGroupWithSourceModel._meta.options.get('rules'):
            with self.subTest(rule=rule):
                result = rule.run(subject_visit)
                if rule.name == 'crfs_male':
                    self.assertEqual(
                        result,
                        {'edc_metadata.crffive': REQUIRED,
                         'edc_metadata.crffour': REQUIRED})
                elif rule.name == 'crfs_female':
                    self.assertEqual(
                        result,
                        {'edc_metadata.crfthree': NOT_REQUIRED,
                         'edc_metadata.crftwo': NOT_REQUIRED})

    def test_rules_run_if_source_f1_equals_bicycle(self):
        subject_visit = self.enroll(MALE)
        CrfOne.objects.create(subject_visit=subject_visit, f1='bicycle')
        for rule in CrfRuleGroupWithSourceModel._meta.options.get('rules'):
            with self.subTest(rule=rule):
                result = rule.run(subject_visit)
                if rule.name == 'crfs_male':
                    self.assertEqual(
                        result,
                        {'edc_metadata.crffive': NOT_REQUIRED,
                         'edc_metadata.crffour': NOT_REQUIRED})
                elif rule.name == 'crfs_female':
                    self.assertEqual(
                        result,
                        {'edc_metadata.crfthree': REQUIRED,
                         'edc_metadata.crftwo': REQUIRED})

    def test_rules_run_requires_registered_subject(self):
        subject_visit = self.enroll(MALE)
        RegisteredSubject.objects.all().delete()
        for rule in CrfRuleGroupWithSourceModel._meta.options.get('rules'):
            self.assertRaises(
                RuleEvaluatorRegisterSubjectError,
                rule.run, subject_visit)

    def test_metadata_rules_run_male_required(self):
        subject_visit = self.enroll(gender=MALE)
        for target_model in ['edc_metadata.crffour', 'edc_metadata.crffive']:
            with self.subTest(target_model=target_model):
                obj = CrfMetadata.objects.get(
                    model=target_model,
                    subject_identifier=subject_visit.subject_identifier,
                    visit_code=subject_visit.visit_code)
                self.assertEqual(obj.entry_status, REQUIRED)

    def test_metadata_rules_run_female_required(self):
        subject_visit = self.enroll(gender=FEMALE)
        for target_model in ['edc_metadata.crftwo', 'edc_metadata.crfthree']:
            with self.subTest(target_model=target_model):
                obj = CrfMetadata.objects.get(
                    model=target_model,
                    subject_identifier=subject_visit.subject_identifier,
                    visit_code=subject_visit.visit_code)
                self.assertEqual(obj.entry_status, REQUIRED)

    def test_metadata_rules_run_female_not_required(self):
        subject_visit = self.enroll(gender=FEMALE)
        for target_model in ['edc_metadata.crffour', 'edc_metadata.crffive']:
            with self.subTest(target_model=target_model):
                obj = CrfMetadata.objects.get(
                    model=target_model,
                    subject_identifier=subject_visit.subject_identifier,
                    visit_code=subject_visit.visit_code)
                self.assertEqual(obj.entry_status, NOT_REQUIRED)

    def test_metadata_rules_run_male_not_required(self):
        subject_visit = self.enroll(gender=MALE)
        for target_model in ['edc_metadata.crftwo', 'edc_metadata.crfthree']:
            with self.subTest(target_model=target_model):
                obj = CrfMetadata.objects.get(
                    model=target_model,
                    subject_identifier=subject_visit.subject_identifier,
                    visit_code=subject_visit.visit_code)
                self.assertEqual(obj.entry_status, NOT_REQUIRED)

    def test_rule_group_metadata_objects(self):
        subject_visit = self.enroll(gender=MALE)
        _, metadata_objects = CrfRuleGroupGender().evaluate_rules(visit=subject_visit)
        self.assertEqual(metadata_objects.get(
            'edc_metadata.crffour').entry_status, REQUIRED)
        self.assertEqual(metadata_objects.get(
            'edc_metadata.crffive').entry_status, REQUIRED)
        self.assertEqual(metadata_objects.get(
            'edc_metadata.crftwo').entry_status, NOT_REQUIRED)
        self.assertEqual(metadata_objects.get(
            'edc_metadata.crfthree').entry_status, NOT_REQUIRED)

    def test_rule_group_rule_results(self):
        subject_visit = self.enroll(gender=MALE)
        rule_results, _ = CrfRuleGroupGender().evaluate_rules(visit=subject_visit)
        self.assertEqual(rule_results['CrfRuleGroupGender.crfs_male'].get(
            'edc_metadata.crffour'), REQUIRED)
        self.assertEqual(rule_results['CrfRuleGroupGender.crfs_male'].get(
            'edc_metadata.crffive'), REQUIRED)
        self.assertEqual(rule_results['CrfRuleGroupGender.crfs_female'].get(
            'edc_metadata.crftwo'), NOT_REQUIRED)
        self.assertEqual(rule_results['CrfRuleGroupGender.crfs_female'].get(
            'edc_metadata.crfthree'), NOT_REQUIRED)

    @tag('1')
    def test_bad_rule_group_target_model(self):

        site_metadata_rules.registry = OrderedDict()
        subject_visit = self.enroll(gender=MALE)

        class BadCrfRuleGroup(RuleGroup):
            crfs_male = CrfRule(
                logic=Logic(
                    predicate=P('f1', 'eq', 'car'),
                    consequence=REQUIRED,
                    alternative=NOT_REQUIRED),
                target_models=['blah'])

            class Meta:
                app_label = 'edc_metadata'
                source_model = 'edc_metadata.crfone'
        self.assertRaises(
            TargetModelLookupError,
            BadCrfRuleGroup().evaluate_rules, visit=subject_visit)

    def test_bad_rule_group_target_model_cannot_also_be_source_model(self):

        site_metadata_rules.registry = OrderedDict()

        try:
            class BadCrfRuleGroup(RuleGroup):
                crfs_male = CrfRule(
                    logic=Logic(
                        predicate=P('f1', 'eq', 'car'),
                        consequence=REQUIRED,
                        alternative=NOT_REQUIRED),
                    target_models=['crfone'])

                class Meta:
                    app_label = 'edc_metadata'
                    source_model = 'edc_metadata.crfone'
        except RuleGroupModelConflict:
            pass
        else:
            self.fail('RuleGroupModelConflict not raised.')

    def test_rule_group_target_model_cannot_be_visit_model(self):
        site_metadata_rules.registry = OrderedDict()

        subject_visit = self.enroll(gender=MALE)

        class BadCrfRuleGroup(RuleGroup):
            rule = CrfRule(
                logic=Logic(
                    predicate=P('f1', 'eq', 'car'),
                    consequence=REQUIRED,
                    alternative=NOT_REQUIRED),
                target_models=['subjectvisit'])

            class Meta:
                app_label = 'edc_metadata'
                source_model = 'edc_metadata.crfone'
        self.assertRaises(
            TargetModelConflict,
            BadCrfRuleGroup().evaluate_rules, visit=subject_visit)

    def test_bad_predicate_blah_is_not_an_operator(self):
        try:
            class BadCrfRuleGroup(RuleGroup):
                rule = CrfRule(
                    logic=Logic(
                        predicate=P('f1', 'blah', 'car'),
                        consequence=REQUIRED,
                        alternative=NOT_REQUIRED),
                    target_models=['crftwo'])

                class Meta:
                    app_label = 'edc_metadata'
                    source_model = 'edc_metadata.crfone'
        except PredicateError:
            pass
        else:
            self.fail('PredicateError not raised.')

    def test_bad_predicate_blah_is_not_a_valid_attr(self):
        subject_visit = self.enroll(gender=MALE)

        class BadCrfRuleGroup(RuleGroup):
            rule = CrfRule(
                logic=Logic(
                    predicate=P('blah', 'eq', 'car'),
                    consequence=REQUIRED,
                    alternative=NOT_REQUIRED),
                target_models=['crftwo'])

            class Meta:
                app_label = 'edc_metadata'
                source_model = 'edc_metadata.crfone'

        self.assertRaises(
            RuleEvaluatorError,
            BadCrfRuleGroup().evaluate_rules, visit=subject_visit)

    @tag('3')
    def test_predicate_pf(self):
        """Asserts entry status unchanged if source model does not exist.
        """
        def func(f1, f2):
            return True if f1 == 'f1' and f2 == 'f2' else False

        class CrfRuleGroup(RuleGroup):
            rule = CrfRule(
                logic=Logic(
                    predicate=PF('f1', 'f2', func=func),
                    consequence=REQUIRED,
                    alternative=NOT_REQUIRED),
                target_models=['crftwo'])

            class Meta:
                app_label = 'edc_metadata'
                source_model = 'edc_metadata.crfone'

        site_metadata_rules.registry = OrderedDict()
        subject_visit = self.enroll(gender=MALE)

        CrfRuleGroup().evaluate_rules(visit=subject_visit)

        obj = CrfMetadata.objects.get(
            model='edc_metadata.crftwo',
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code)
        self.assertEqual(obj.entry_status, REQUIRED)

    @tag('3')
    def test_predicate_pf2(self):
        """Asserts entry status set to alternative if source model
        exists but does not meet criteria.
        """
        def func(f1, f2):
            return True if f1 == 'f1' and f2 == 'f2' else False

        class CrfRuleGroup(RuleGroup):
            rule = CrfRule(
                logic=Logic(
                    predicate=PF('f1', 'f2', func=func),
                    consequence=REQUIRED,
                    alternative=NOT_REQUIRED),
                target_models=['crftwo'])

            class Meta:
                app_label = 'edc_metadata'
                source_model = 'edc_metadata.crfone'

        site_metadata_rules.registry = OrderedDict()
        subject_visit = self.enroll(gender=MALE)
        CrfOne.objects.create(subject_visit=subject_visit)
        CrfRuleGroup().evaluate_rules(visit=subject_visit)

        obj = CrfMetadata.objects.get(
            model='edc_metadata.crftwo',
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code)
        self.assertEqual(obj.entry_status, NOT_REQUIRED)

    @tag('3')
    def test_predicate_pf3(self):
        """Asserts entry status set to consequence if source model
        exists and meets criteria.
        """
        def func(f1, f2):
            return True if f1 == 'f1' and f2 == 'f2' else False

        class CrfRuleGroup(RuleGroup):
            rule = CrfRule(
                logic=Logic(
                    predicate=PF('f1', 'f2', func=func),
                    consequence=REQUIRED,
                    alternative=NOT_REQUIRED),
                target_models=['crftwo'])

            class Meta:
                app_label = 'edc_metadata'
                source_model = 'edc_metadata.crfone'

        site_metadata_rules.registry = OrderedDict()
        subject_visit = self.enroll(gender=MALE)
        CrfOne.objects.create(subject_visit=subject_visit, f1='f1', f2='f2')
        CrfRuleGroup().evaluate_rules(visit=subject_visit)

        obj = CrfMetadata.objects.get(
            model='edc_metadata.crftwo',
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code)
        self.assertEqual(obj.entry_status, REQUIRED)

    @tag('3')
    def test_predicate_pf4(self):
        """Asserts raises on bad attr.
        """
        def func(f1, f2):
            return True if f1 == 'f1' and f2 == 'f2' else False

        class CrfRuleGroup(RuleGroup):
            rule = CrfRule(
                logic=Logic(
                    predicate=PF('blah', 'f2', func=func),
                    consequence=REQUIRED,
                    alternative=NOT_REQUIRED),
                target_models=['crftwo'])

            class Meta:
                app_label = 'edc_metadata'
                source_model = 'edc_metadata.crfone'
        site_metadata_rules.registry = OrderedDict()
        subject_visit = self.enroll(gender=MALE)
        self.assertRaises(
            RuleEvaluatorError,
            CrfRuleGroup().evaluate_rules, visit=subject_visit)

    def test_p_repr(self):

        p = P('blah', 'eq', 'car')
        self.assertTrue(repr(p))

    def test_pf_repr(self):

        def func(f1, f2):
            return True if f1 == 'f1' and f2 == 'f2' else False
        pf = PF('blah', 'f2', func=func)
        self.assertTrue(repr(pf))

    def test_rule_repr(self):
        rule = CrfRule(
            logic=Logic(
                predicate=P('f1', 'eq', 'car'),
                consequence=REQUIRED,
                alternative=NOT_REQUIRED),
            target_models=['crftwo'])
        self.assertTrue(repr(rule))

    def test_target_model_missing_manager(self):
        class BadCrfRuleGroup(RuleGroup):
            rule = CrfRule(
                logic=Logic(
                    predicate=P('f1', 'eq', 'car'),
                    consequence=REQUIRED,
                    alternative=NOT_REQUIRED),
                target_models=['crfmissingmanager'])

            class Meta:
                app_label = 'edc_metadata'
                source_model = 'edc_metadata.crfone'

        site_metadata_rules.registry = OrderedDict()
        subject_visit = self.enroll(gender=MALE)
        self.assertRaises(
            TargetModelMissingManagerMethod,
            BadCrfRuleGroup().evaluate_rules, visit=subject_visit)

    def test_target_model(self):
        """Assert can declare a single target model as \'target_model\'
        instead of a list of \'target_models\'.
        """
        class CrfRuleGroup(RuleGroup):
            rule = CrfRule(
                logic=Logic(
                    predicate=P('f1', 'eq', 'car'),
                    consequence=REQUIRED,
                    alternative=NOT_REQUIRED),
                target_model='crftwo')  # diff is here

            class Meta:
                app_label = 'edc_metadata'
                source_model = 'edc_metadata.crfone'

        site_metadata_rules.registry = OrderedDict()
        subject_visit = self.enroll(gender=MALE)
        CrfRuleGroup().evaluate_rules(visit=subject_visit)
        obj = CrfMetadata.objects.get(
            model='edc_metadata.crftwo',
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code)
        self.assertEqual(obj.entry_status, REQUIRED)

    def test_rule_group_meta_repr(self):

        class CrfRuleGroup(RuleGroup):
            rule = CrfRule(
                logic=Logic(
                    predicate=P('f1', 'eq', 'car'),
                    consequence=REQUIRED,
                    alternative=NOT_REQUIRED),
                target_models=['crftwo'])

            class Meta:
                app_label = 'edc_metadata'
                source_model = 'edc_metadata.crfmissingmanager'
        self.assertTrue(repr(CrfRuleGroup()._meta))

    def test_source_model_missing_manager(self):
        class CrfRuleGroup(RuleGroup):
            rule = CrfRule(
                logic=Logic(
                    predicate=P('f1', 'eq', 'car'),
                    consequence=REQUIRED,
                    alternative=NOT_REQUIRED),
                target_models=['crftwo'])

            class Meta:
                app_label = 'edc_metadata'
                source_model = 'edc_metadata.crfmissingmanager'

        site_metadata_rules.registry = OrderedDict()
        subject_visit = self.enroll(gender=MALE)
        self.assertRaises(
            RuleEvaluatorError,
            CrfRuleGroup().evaluate_rules, visit=subject_visit)

    def test_sub_class_rule_group(self):

        class CrfRuleGroup(RuleGroup):
            rule1 = CrfRule(
                logic=Logic(
                    predicate=P('f1', 'eq', 'car'),
                    consequence=REQUIRED,
                    alternative=NOT_REQUIRED),
                target_models=['crftwo'])

            class Meta:
                abstract = True

        class NewCrfRuleGroup(CrfRuleGroup):

            rule2 = CrfRule(
                logic=Logic(
                    predicate=P('f1', 'eq', 'car'),
                    consequence=REQUIRED,
                    alternative=NOT_REQUIRED),
                target_models=['crfthree'])

            class Meta:
                app_label = 'edc_metadata'
                source_model = 'edc_metadata.crfmissingmanager'

        self.assertTrue(len(NewCrfRuleGroup()._meta.options.get('rules')), 2)

    def test_rule_group_missing_meta(self):

        try:
            class CrfRuleGroup(RuleGroup):
                rule1 = CrfRule(
                    logic=Logic(
                        predicate=P('f1', 'eq', 'car'),
                        consequence=REQUIRED,
                        alternative=NOT_REQUIRED),
                    target_models=['crftwo'])

        except AttributeError:
            pass
        else:
            self.fail('AttributeError not raised.')

    def test_rule_group_invalid_meta_option(self):

        try:
            class CrfRuleGroup(RuleGroup):
                rule1 = CrfRule(
                    logic=Logic(
                        predicate=P('f1', 'eq', 'car'),
                        consequence=REQUIRED,
                        alternative=NOT_REQUIRED),
                    target_models=['crftwo'])

                class Meta:
                    app_label = 'edc_metadata'
                    source_model = 'edc_metadata.crfmissingmanager'
                    blah = 'blah'

        except RuleGroupMetaError:
            pass
        else:
            self.fail('AttributeError not raised.')
