from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from django.test import TestCase, override_settings
from faker import Faker

from edc_consent import site_consents
from edc_constants.constants import MALE
from edc_facility.import_holidays import import_holidays
from edc_metadata.constants import NOT_REQUIRED, REQUIRED
from edc_metadata.metadata_rules import (
    PF,
    CrfRule,
    CrfRuleGroup,
    CrfRuleModelConflict,
    P,
    PredicateError,
    RuleEvaluatorRegisterSubjectError,
    RuleGroupMetaError,
    TargetModelConflict,
    site_metadata_rules,
)
from edc_metadata.models import CrfMetadata
from edc_registration.models import RegisteredSubject
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import CrfThree
from clinicedc_tests.visit_schedules.visit_schedule_metadata.visit_schedule import (
    get_visit_schedule,
)

from ..crf_rule_groups import (
    CrfRuleGroupGender,
    CrfRuleGroupWithoutExplicitReferenceModel,
    CrfRuleGroupWithoutSourceModel,
    CrfRuleGroupWithSourceModel,
)

fake = Faker()
utc_tz = ZoneInfo("UTC")


@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=utc_tz))
class TestMetadataRulesWithGender(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        self.helper = Helper()
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(get_visit_schedule(consent_v1))
        # note crfs in visit schedule are all set to REQUIRED by default.
        _, self.schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_visit_schedule.onschedule"
        )

        site_metadata_rules.registry = {}
        site_metadata_rules.register(rule_group_cls=CrfRuleGroupGender)

    def test_rules_with_source_model(self):
        for rule in CrfRuleGroupWithSourceModel._meta.options.get("rules"):
            self.assertEqual(rule.source_model, "clinicedc_tests.crfone")

    def test_rules_without_source_model(self):
        for rule in CrfRuleGroupWithoutSourceModel._meta.options.get("rules"):
            self.assertIsNone(rule.source_model)

    def test_rules_source_and_reference_model_is_none(self):
        subject_visit = self.helper.enroll_to_baseline(gender=MALE)
        for rule in CrfRuleGroupWithoutSourceModel._meta.options.get("rules"):
            with self.subTest(rule=rule):
                result = rule.run(subject_visit)
                if rule.name == "crfs_male":
                    self.assertEqual(
                        result,
                        {
                            "clinicedc_tests.crfseven": REQUIRED,
                            "clinicedc_tests.crfsix": REQUIRED,
                        },
                    )
                elif rule.name == "crfs_female":
                    self.assertEqual(
                        result,
                        {
                            "clinicedc_tests.crffive": NOT_REQUIRED,
                            "clinicedc_tests.crffour": NOT_REQUIRED,
                        },
                    )

    def test_rules_with_source_but_no_explicit_reference_model(self):
        subject_visit = self.helper.enroll_to_baseline(gender=MALE)
        for rule in CrfRuleGroupWithoutExplicitReferenceModel._meta.options.get(
            "rules"
        ):
            with self.subTest(rule=rule):
                self.assertIsNotNone(rule.source_model)
                result = rule.run(subject_visit)
                if rule.name == "crfs_male":
                    self.assertEqual(
                        result,
                        {
                            "clinicedc_tests.crfseven": REQUIRED,
                            "clinicedc_tests.crfsix": REQUIRED,
                        },
                    )
                elif rule.name == "crfs_female":
                    self.assertEqual(
                        result,
                        {
                            "clinicedc_tests.crffive": NOT_REQUIRED,
                            "clinicedc_tests.crffour": NOT_REQUIRED,
                        },
                    )

    def test_rules_if_no_source_model_instance(self):
        subject_visit = self.helper.enroll_to_baseline(gender=MALE)
        for rule in CrfRuleGroupWithSourceModel._meta.options.get("rules"):
            with self.subTest(rule=rule):
                result = rule.run(subject_visit)
                if rule.name == "crfs_male":
                    self.assertEqual(
                        result,
                        {
                            "clinicedc_tests.crfseven": NOT_REQUIRED,
                            "clinicedc_tests.crfsix": NOT_REQUIRED,
                        },
                    )
                elif rule.name == "crfs_female":
                    self.assertEqual(
                        result,
                        {
                            "clinicedc_tests.crffive": NOT_REQUIRED,
                            "clinicedc_tests.crffour": NOT_REQUIRED,
                        },
                    )

    def test_rules_run_if_source_f1_equals_car(self):
        subject_visit = self.helper.enroll_to_baseline(gender=MALE)
        CrfThree.objects.create(subject_visit=subject_visit, f1="car")
        for rule in CrfRuleGroupWithSourceModel._meta.options.get("rules"):
            with self.subTest(rule=rule):
                result = rule.run(subject_visit)
                if rule.name == "crfs_male":
                    self.assertEqual(
                        result,
                        {
                            "clinicedc_tests.crfseven": REQUIRED,
                            "clinicedc_tests.crfsix": REQUIRED,
                        },
                    )
                elif rule.name == "crfs_female":
                    self.assertEqual(
                        result,
                        {
                            "clinicedc_tests.crffive": NOT_REQUIRED,
                            "clinicedc_tests.crffour": NOT_REQUIRED,
                        },
                    )

    def test_rules_run_if_source_f1_equals_bicycle(self):
        subject_visit = self.helper.enroll_to_baseline(gender=MALE)
        CrfThree.objects.create(subject_visit=subject_visit, f1="bicycle")
        for rule in CrfRuleGroupWithSourceModel._meta.options.get("rules"):
            with self.subTest(rule=rule):
                result = rule.run(subject_visit)
                if rule.name == "crfs_male":
                    self.assertEqual(
                        result,
                        {
                            "clinicedc_tests.crfseven": NOT_REQUIRED,
                            "clinicedc_tests.crfsix": NOT_REQUIRED,
                        },
                    )
                elif rule.name == "crfs_female":
                    self.assertEqual(
                        result,
                        {
                            "clinicedc_tests.crffive": REQUIRED,
                            "clinicedc_tests.crffour": REQUIRED,
                        },
                    )

    def test_rules_run_requires_registered_subject(self):
        subject_visit = self.helper.enroll_to_baseline(gender=MALE)
        RegisteredSubject.objects.all().delete()
        for rule in CrfRuleGroupWithSourceModel._meta.options.get("rules"):
            self.assertRaises(
                RuleEvaluatorRegisterSubjectError, rule.run, subject_visit
            )

    def test_metadata_rules_run_male_required(self):
        subject_visit = self.helper.enroll_to_baseline(gender=MALE)
        for target_model in [
            "clinicedc_tests.crfsix",
            "clinicedc_tests.crfseven",
        ]:
            with self.subTest(target_model=target_model):
                obj = CrfMetadata.objects.get(
                    model=target_model,
                    subject_identifier=subject_visit.subject_identifier,
                    visit_code=subject_visit.visit_code,
                )
                self.assertEqual(obj.entry_status, REQUIRED)

    def test_metadata_rules_run_female_required(self):
        subject_visit = self.helper.enroll_to_baseline(gender=MALE)
        for target_model in [
            "clinicedc_tests.crffour",
            "clinicedc_tests.crffive",
        ]:
            with self.subTest(target_model=target_model):
                obj = CrfMetadata.objects.get(
                    model=target_model,
                    subject_identifier=subject_visit.subject_identifier,
                    visit_code=subject_visit.visit_code,
                )
                self.assertEqual(obj.entry_status, REQUIRED)

    def test_metadata_rules_run_female_not_required(self):
        subject_visit = self.helper.enroll_to_baseline(gender=MALE)
        for target_model in [
            "clinicedc_tests.crfsix",
            "clinicedc_tests.crfseven",
        ]:
            with self.subTest(target_model=target_model):
                obj = CrfMetadata.objects.get(
                    model=target_model,
                    subject_identifier=subject_visit.subject_identifier,
                    visit_code=subject_visit.visit_code,
                )
                self.assertEqual(obj.entry_status, NOT_REQUIRED)

    def test_metadata_rules_run_male_not_required(self):
        subject_visit = self.helper.enroll_to_baseline(gender=MALE)
        for target_model in [
            "clinicedc_tests.crffour",
            "clinicedc_tests.crffive",
        ]:
            with self.subTest(target_model=target_model):
                obj = CrfMetadata.objects.get(
                    model=target_model,
                    subject_identifier=subject_visit.subject_identifier,
                    visit_code=subject_visit.visit_code,
                )
                self.assertEqual(obj.entry_status, NOT_REQUIRED)

    def test_rule_group_metadata_objects(self):
        subject_visit = self.helper.enroll_to_baseline(gender=MALE)
        _, metadata_objects = CrfRuleGroupGender().evaluate_rules(
            related_visit=subject_visit
        )
        self.assertEqual(
            metadata_objects.get("clinicedc_tests.crfsix").entry_status, REQUIRED
        )
        self.assertEqual(
            metadata_objects.get("clinicedc_tests.crfseven").entry_status, REQUIRED
        )
        self.assertEqual(
            metadata_objects.get("clinicedc_tests.crffour").entry_status, NOT_REQUIRED
        )
        self.assertEqual(
            metadata_objects.get("clinicedc_tests.crffive").entry_status,
            NOT_REQUIRED,
        )

    def test_rule_group_rule_results(self):
        subject_visit = self.helper.enroll_to_baseline(gender=MALE)
        rule_results, _ = CrfRuleGroupGender().evaluate_rules(
            related_visit=subject_visit
        )
        self.assertEqual(
            rule_results["CrfRuleGroupGender.crfs_male"].get("clinicedc_tests.crfsix"),
            REQUIRED,
        )
        self.assertEqual(
            rule_results["CrfRuleGroupGender.crfs_male"].get(
                "clinicedc_tests.crfseven"
            ),
            REQUIRED,
        )
        self.assertEqual(
            rule_results["CrfRuleGroupGender.crfs_female"].get(
                "clinicedc_tests.crffour"
            ),
            NOT_REQUIRED,
        )
        self.assertEqual(
            rule_results["CrfRuleGroupGender.crfs_female"].get(
                "clinicedc_tests.crffive"
            ),
            NOT_REQUIRED,
        )

    def test_bad_rule_group_target_model_cannot_also_be_source_model(self):
        site_metadata_rules.registry = {}
        subject_visit = self.helper.enroll_to_baseline(gender=MALE)

        class BadCrfRuleGroup(CrfRuleGroup):
            crfs_male = CrfRule(
                predicate=P("f1", "eq", "car"),
                consequence=REQUIRED,
                alternative=NOT_REQUIRED,
                target_models=["crfthree"],
            )

            class Meta:
                app_label = "edc_metadata"
                source_model = "clinicedc_tests.crfthree"
                related_visit_model = "edc_visit_tracking.subjectvisit"

        self.assertRaises(
            CrfRuleModelConflict,
            BadCrfRuleGroup().evaluate_rules,
            related_visit=subject_visit,
        )

    def test_rule_group_target_model_cannot_be_visit_model(self):
        site_metadata_rules.registry = {}

        subject_visit = self.helper.enroll_to_baseline(gender=MALE)

        class BadCrfRuleGroup(CrfRuleGroup):
            rule = CrfRule(
                predicate=P("f1", "eq", "car"),
                consequence=REQUIRED,
                alternative=NOT_REQUIRED,
                target_models=["subjectvisit"],
            )

            class Meta:
                app_label = "edc_metadata"
                source_model = "clinicedc_tests.crfthree"
                related_visit_model = "edc_visit_tracking.subjectvisit"

        self.assertRaises(
            TargetModelConflict,
            BadCrfRuleGroup().evaluate_rules,
            related_visit=subject_visit,
        )

    def test_bad_predicate_blah_is_not_an_operator(self):
        try:

            class BadCrfRuleGroup(CrfRuleGroup):
                rule = CrfRule(
                    predicate=P("f1", "blah", "car"),
                    consequence=REQUIRED,
                    alternative=NOT_REQUIRED,
                    target_models=["crffour"],
                )

                class Meta:
                    app_label = "edc_metadata"
                    source_model = "clinicedc_tests.crfthree"
                    related_visit_model = "edc_visit_tracking.subjectvisit"

        except PredicateError:
            pass
        else:
            self.fail("PredicateError not raised.")

    def test_predicate_pf(self):
        def func(f1, f2):
            return True if f1 == "f1" and f2 == "f2" else False

        class MyCrfRuleGroup(CrfRuleGroup):
            rule = CrfRule(
                predicate=PF("f1", "f2", func=func),
                consequence=REQUIRED,
                alternative=NOT_REQUIRED,
                target_models=["crffour"],
            )

            class Meta:
                app_label = "edc_metadata"
                source_model = "clinicedc_tests.crfthree"
                related_visit_model = "edc_visit_tracking.subjectvisit"

        site_metadata_rules.registry = {}
        site_metadata_rules.register(MyCrfRuleGroup)
        subject_visit = self.helper.enroll_to_baseline(gender=MALE)

        MyCrfRuleGroup().evaluate_rules(related_visit=subject_visit)

        obj = CrfMetadata.objects.get(
            model="clinicedc_tests.crffour",
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code,
        )
        self.assertEqual(obj.entry_status, NOT_REQUIRED)

    @override_settings(DEBUG=True)
    def test_predicate_pf2(self):
        """Asserts entry status set to alternative if source model
        exists but does not meet criteria.
        """

        def func(f1, f2):
            return f1 == "f1_value" and f2 == "f2_value"

        class MyCrfRuleGroup(CrfRuleGroup):
            rule = CrfRule(
                predicate=PF("f1", "f2", func=func),
                consequence=REQUIRED,
                alternative=NOT_REQUIRED,
                target_models=["crffour"],
            )

            class Meta:
                app_label = "edc_metadata"
                source_model = "clinicedc_tests.crfthree"
                related_visit_model = "edc_visit_tracking.subjectvisit"

        site_metadata_rules.registry = {}
        site_metadata_rules.register(MyCrfRuleGroup)
        subject_visit = self.helper.enroll_to_baseline(gender=MALE)
        obj = CrfMetadata.objects.get(
            model="clinicedc_tests.crffour",
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code,
        )
        self.assertEqual(obj.entry_status, NOT_REQUIRED)
        CrfThree.objects.create(subject_visit=subject_visit, f1="blah", f2="f2_value")
        self.assertFalse(func("blah", "f2_value"))
        # MyCrfRuleGroup().evaluate_rules(related_visit=subject_visit)
        obj = CrfMetadata.objects.get(
            model="clinicedc_tests.crffour",
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code,
        )

        self.assertEqual(obj.entry_status, NOT_REQUIRED)

    def test_predicate_pf3(self):
        """Asserts entry status set to consequence if source model
        exists and meets criteria.
        """

        def func(f1, f2):
            return True if f1 == "f1" and f2 == "f2" else False

        class MyCrfRuleGroup(CrfRuleGroup):
            rule = CrfRule(
                predicate=PF("f1", "f2", func=func),
                consequence=REQUIRED,
                alternative=NOT_REQUIRED,
                target_models=["crffour"],
            )

            class Meta:
                app_label = "edc_metadata"
                source_model = "clinicedc_tests.crfthree"
                related_visit_model = "edc_visit_tracking.subjectvisit"

        site_metadata_rules.registry = {}
        subject_visit = self.helper.enroll_to_baseline(gender=MALE)
        CrfThree.objects.create(subject_visit=subject_visit, f1="f1", f2="f2")
        MyCrfRuleGroup().evaluate_rules(related_visit=subject_visit)

        obj = CrfMetadata.objects.get(
            model="clinicedc_tests.crffour",
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code,
        )
        self.assertEqual(obj.entry_status, REQUIRED)

    def test_p_repr(self):
        p = P("blah", "eq", "car")
        self.assertTrue(repr(p))

    def test_pf_repr(self):
        def func(f1, f2):
            return True if f1 == "f1" and f2 == "f2" else False

        pf = PF("blah", "f2", func=func)
        self.assertTrue(repr(pf))

    def test_rule_repr(self):
        rule = CrfRule(
            predicate=P("f1", "eq", "car"),
            consequence=REQUIRED,
            alternative=NOT_REQUIRED,
            target_models=["crffour"],
        )
        self.assertTrue(repr(rule))

    def test_rule_group_meta_repr(self):
        class MyCrfRuleGroup(CrfRuleGroup):
            rule = CrfRule(
                predicate=P("f1", "eq", "car"),
                consequence=REQUIRED,
                alternative=NOT_REQUIRED,
                target_models=["crffour"],
            )

            class Meta:
                app_label = "edc_metadata"
                source_model = "clinicedc_tests.crfmissingmanager"
                related_visit_model = "edc_visit_tracking.subjectvisit"

        self.assertTrue(repr(MyCrfRuleGroup()._meta))

    def test_sub_class_rule_group(self):
        class MyCrfRuleGroup(CrfRuleGroup):
            rule1 = CrfRule(
                predicate=P("f1", "eq", "car"),
                consequence=REQUIRED,
                alternative=NOT_REQUIRED,
                target_models=["crffour"],
            )

            class Meta:
                abstract = True

        class NewCrfRuleGroup(CrfRuleGroup):
            rule2 = CrfRule(
                predicate=P("f1", "eq", "car"),
                consequence=REQUIRED,
                alternative=NOT_REQUIRED,
                target_models=["crffive"],
            )

            class Meta:
                app_label = "edc_metadata"
                source_model = "clinicedc_tests.crfmissingmanager"
                related_visit_model = "edc_visit_tracking.subjectvisit"

        self.assertTrue(len(NewCrfRuleGroup()._meta.options.get("rules")), 2)

    def test_rule_group_missing_meta(self):
        try:

            class MyCrfRuleGroup(CrfRuleGroup):
                rule1 = CrfRule(
                    predicate=P("f1", "eq", "car"),
                    consequence=REQUIRED,
                    alternative=NOT_REQUIRED,
                    target_models=["crffour"],
                )

        except AttributeError:
            pass
        else:
            self.fail("AttributeError not raised.")

    def test_rule_group_invalid_meta_option(self):
        try:

            class MyCrfRuleGroup(CrfRuleGroup):
                rule1 = CrfRule(
                    predicate=P("f1", "eq", "car"),
                    consequence=REQUIRED,
                    alternative=NOT_REQUIRED,
                    target_models=["crffour"],
                )

                class Meta:
                    app_label = "edc_metadata"
                    source_model = "clinicedc_tests.crfmissingmanager"
                    related_visit_model = "edc_visit_tracking.subjectvisit"
                    blah = "blah"

        except RuleGroupMetaError:
            pass
        else:
            self.fail("AttributeError not raised.")
