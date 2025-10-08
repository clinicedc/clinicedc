from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import CrfOne, SubjectRequisition
from clinicedc_tests.visit_schedules.visit_schedule_metadata.visit_schedule import (
    get_visit_schedule,
)
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, override_settings, tag
from faker import Faker

from edc_consent import site_consents
from edc_constants.constants import FEMALE, MALE
from edc_facility.import_holidays import import_holidays
from edc_lab.models import Panel
from edc_metadata.constants import KEYED, NOT_REQUIRED, REQUIRED
from edc_metadata.metadata_rules import (
    P,
    RequisitionRule,
    RequisitionRuleGroup,
    RequisitionRuleGroupMetaOptionsError,
    site_metadata_rules,
)
from edc_metadata.models import RequisitionMetadata
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

test_datetime = datetime(2019, 6, 11, 8, 00, tzinfo=ZoneInfo("UTC"))

fake = Faker()


class RequisitionPanel:
    def __init__(self, name):
        self.name = name


panel_one = RequisitionPanel("one")
panel_two = RequisitionPanel("two")
panel_three = RequisitionPanel("three")
panel_four = RequisitionPanel("four")
panel_five = RequisitionPanel("five")
panel_six = RequisitionPanel("six")
panel_seven = RequisitionPanel("seven")
panel_eight = RequisitionPanel("eight")


class BadPanelsRequisitionRuleGroup(RequisitionRuleGroup):
    """Specifies invalid panel names."""

    rule = RequisitionRule(
        predicate=P("gender", "eq", MALE),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_panels=["blah1", "blah2"],
    )

    class Meta:
        app_label = "clinicedc_tests"
        source_model = "clinicedc_tests.crfone"
        requisition_model = "subjectrequisition"


class RequisitionRuleGroup2(RequisitionRuleGroup):
    """A rule group where source model is a requisition.

    If male, panel_one and panel_two are required.
    If female, panel_three and panel_four are required.
    """

    male = RequisitionRule(
        predicate=P("gender", "eq", MALE),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        source_panel=panel_five,
        target_panels=[panel_one, panel_two],
    )

    female = RequisitionRule(
        predicate=P("gender", "eq", FEMALE),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        source_panel=panel_six,
        target_panels=[panel_three, panel_four],
    )

    class Meta:
        app_label = "clinicedc_tests"
        source_model = "subjectrequisition"
        requisition_model = "subjectrequisition"


class RequisitionRuleGroup3(RequisitionRuleGroup):
    """A rule group where source model is a requisition."""

    female = RequisitionRule(
        predicate=P("f1", "eq", "hello"),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_panels=[panel_six, panel_seven, panel_eight],
    )

    class Meta:
        app_label = "clinicedc_tests"
        source_model = "crfone"
        requisition_model = "subjectrequisition"


class BaseRequisitionRuleGroup(RequisitionRuleGroup):
    male = RequisitionRule(
        predicate=P("gender", "eq", MALE),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_panels=[panel_one, panel_two],
    )

    female = RequisitionRule(
        predicate=P("gender", "eq", FEMALE),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_panels=[panel_three, panel_four],
    )

    class Meta:
        abstract = True


class MyRequisitionRuleGroup(BaseRequisitionRuleGroup):
    """A rule group where source model is NOT a requisition."""

    class Meta:
        app_label = "clinicedc_tests"
        source_model = "crfone"
        requisition_model = "subjectrequisition"


utc_tz = ZoneInfo("UTC")


@tag("metadata")
@override_settings(SITE_ID=10)
@time_machine.travel(datetime(2019, 8, 11, 8, 00, tzinfo=utc_tz))
class TestRequisitionRuleGroup(TestCase):
    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super().setUpClass()

    def setUp(self):
        self.panel_one = Panel.objects.create(name=panel_one.name)
        self.panel_two = Panel.objects.create(name=panel_two.name)
        self.panel_three = Panel.objects.create(name=panel_three.name)
        self.panel_four = Panel.objects.create(name=panel_four.name)
        self.panel_five = Panel.objects.create(name=panel_five.name)
        self.panel_six = Panel.objects.create(name=panel_six.name)
        self.panel_seven = Panel.objects.create(name=panel_seven.name)
        self.panel_eight = Panel.objects.create(name=panel_eight.name)

        site_consents.registry = {}
        site_consents.register(consent_v1)

        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        self.visit_schedule = get_visit_schedule(consent_v1)
        site_visit_schedules.register(self.visit_schedule)
        site_metadata_rules.registry = {}

        self.helper = Helper()

    @time_machine.travel(test_datetime)
    def test_rule_male(self):
        subject_visit = self.helper.enroll_to_baseline(
            visit_schedule_name=self.visit_schedule.name, schedule_name="schedule", gender=MALE
        )
        rule_results, _ = MyRequisitionRuleGroup().evaluate_rules(related_visit=subject_visit)
        for panel in [self.panel_one, self.panel_two]:
            with self.subTest(panel=panel):
                key = "clinicedc_tests.subjectrequisition"
                for rule_result in rule_results["MyRequisitionRuleGroup.male"][key]:
                    self.assertEqual(rule_result.entry_status, REQUIRED)
                for rule_result in rule_results["MyRequisitionRuleGroup.female"][key]:
                    self.assertEqual(rule_result.entry_status, NOT_REQUIRED)

    @time_machine.travel(test_datetime)
    def test_rule_female(self):
        subject_visit = self.helper.enroll_to_baseline(
            visit_schedule_name=self.visit_schedule.name,
            schedule_name="schedule",
            gender=FEMALE,
        )
        rule_results, _ = MyRequisitionRuleGroup().evaluate_rules(related_visit=subject_visit)
        for panel in [self.panel_one, self.panel_two]:
            with self.subTest(panel=panel):
                key = "clinicedc_tests.subjectrequisition"
                for rule_result in rule_results["MyRequisitionRuleGroup.female"].get(key):
                    self.assertEqual(rule_result.entry_status, REQUIRED)
                for rule_result in rule_results["MyRequisitionRuleGroup.male"].get(key):
                    self.assertEqual(rule_result.entry_status, NOT_REQUIRED)

    @time_machine.travel(test_datetime)
    def test_source_panel_required_raises(self):
        try:

            class BadRequisitionRuleGroup(BaseRequisitionRuleGroup):
                class Meta:
                    app_label = "clinicedc_tests"
                    source_model = "subjectrequisition"
                    requisition_model = "subjectrequisition"

        except RequisitionRuleGroupMetaOptionsError as e:
            self.assertEqual(e.code, "source_panel_expected")
        else:
            self.fail(
                "RequisitionRuleGroupMetaOptionsError "
                f"not raised for {BadRequisitionRuleGroup}"
            )

    @time_machine.travel(test_datetime)
    def test_source_panel_not_required_raises(self):
        try:

            class BadRequisitionRuleGroup(RequisitionRuleGroup):
                male = RequisitionRule(
                    predicate=P("gender", "eq", MALE),
                    consequence=REQUIRED,
                    alternative=NOT_REQUIRED,
                    source_panel=panel_one,
                    target_panels=[panel_one, panel_two],
                )

                female = RequisitionRule(
                    predicate=P("gender", "eq", FEMALE),
                    consequence=REQUIRED,
                    alternative=NOT_REQUIRED,
                    source_panel=panel_two,
                    target_panels=[panel_three, panel_four],
                )

                class Meta:
                    app_label = "clinicedc_tests"
                    source_model = "crf_one"
                    requisition_model = "subjectrequisition"

        except RequisitionRuleGroupMetaOptionsError as e:
            self.assertEqual(e.code, "source_panel_not_expected")
        else:
            self.fail(
                "RequisitionRuleGroupMetaOptionsError not "
                f"raised for {BadRequisitionRuleGroup}"
            )

    @time_machine.travel(test_datetime)
    def test_rule_male_with_source_model_as_requisition(self):
        subject_visit = self.helper.enroll_to_baseline(
            visit_schedule_name=self.visit_schedule.name, schedule_name="schedule", gender=MALE
        )
        rule_results, _ = RequisitionRuleGroup2().evaluate_rules(related_visit=subject_visit)
        for panel_name in ["one", "two"]:
            with self.subTest(panel_name=panel_name):
                key = "clinicedc_tests.subjectrequisition"
                for rule_result in rule_results["RequisitionRuleGroup2.male"][key]:
                    self.assertEqual(rule_result.entry_status, REQUIRED)
                for rule_result in rule_results["RequisitionRuleGroup2.female"][key]:
                    self.assertEqual(rule_result.entry_status, NOT_REQUIRED)

    @time_machine.travel(test_datetime)
    def test_metadata_for_rule_male_with_source_model_as_requisition1(self):
        """RequisitionRuleGroup2"""
        site_metadata_rules.registry = {}
        site_metadata_rules.register(RequisitionRuleGroup2)
        subject_visit = self.helper.enroll_to_baseline(
            visit_schedule_name=self.visit_schedule.name, schedule_name="schedule", gender=MALE
        )
        SubjectRequisition.objects.create(subject_visit=subject_visit, panel=self.panel_five)
        for panel_name in ["one", "two"]:
            with self.subTest(panel_name=panel_name):
                obj = RequisitionMetadata.objects.get(
                    model="clinicedc_tests.subjectrequisition",
                    subject_identifier=subject_visit.subject_identifier,
                    visit_code=subject_visit.visit_code,
                    panel_name=panel_name,
                )
                self.assertEqual(obj.entry_status, REQUIRED)

    @time_machine.travel(test_datetime)
    def test_metadata_for_rule_male_with_source_model_as_requisition2(self):
        subject_visit = self.helper.enroll_to_baseline(
            visit_schedule_name=self.visit_schedule.name, schedule_name="schedule", gender=MALE
        )
        site_metadata_rules.registry = {}
        site_metadata_rules.register(RequisitionRuleGroup2)
        SubjectRequisition.objects.create(subject_visit=subject_visit, panel=self.panel_five)
        for panel_name in ["three", "four"]:
            with self.subTest(panel_name=panel_name):
                obj = RequisitionMetadata.objects.get(
                    model="clinicedc_tests.subjectrequisition",
                    subject_identifier=subject_visit.subject_identifier,
                    visit_code=subject_visit.visit_code,
                    panel_name=panel_name,
                )
                self.assertEqual(obj.entry_status, NOT_REQUIRED)

    @time_machine.travel(test_datetime)
    def test_metadata_for_rule_female_with_source_model_as_requisition1(self):
        subject_visit = self.helper.enroll_to_baseline(
            visit_schedule_name=self.visit_schedule.name,
            schedule_name="schedule",
            gender=FEMALE,
        )
        site_metadata_rules.registry = {}
        site_metadata_rules.register(RequisitionRuleGroup2)
        SubjectRequisition.objects.create(subject_visit=subject_visit, panel=self.panel_five)
        for panel in [self.panel_three, self.panel_four]:
            with self.subTest(panel=panel):
                obj = RequisitionMetadata.objects.get(
                    model="clinicedc_tests.subjectrequisition",
                    subject_identifier=subject_visit.subject_identifier,
                    visit_code=subject_visit.visit_code,
                    panel_name=panel.name,
                )
                self.assertEqual(obj.entry_status, REQUIRED)

    @time_machine.travel(test_datetime)
    def test_metadata_for_rule_female_with_source_model_as_requisition2(self):
        subject_visit = self.helper.enroll_to_baseline(
            visit_schedule_name=self.visit_schedule.name,
            schedule_name="schedule",
            gender=FEMALE,
        )
        site_metadata_rules.registry = {}
        site_metadata_rules.register(RequisitionRuleGroup2)
        SubjectRequisition.objects.create(subject_visit=subject_visit, panel=self.panel_five)
        for panel in [self.panel_one, self.panel_two]:
            with self.subTest(panel=panel):
                obj = RequisitionMetadata.objects.get(
                    model="clinicedc_tests.subjectrequisition",
                    subject_identifier=subject_visit.subject_identifier,
                    visit_code=subject_visit.visit_code,
                    panel_name=panel.name,
                )
                self.assertEqual(obj.entry_status, NOT_REQUIRED)

    @time_machine.travel(test_datetime)
    def test_metadata_requisition(self):
        site_metadata_rules.registry = {}
        site_metadata_rules.register(RequisitionRuleGroup3)

        subject_visit = self.helper.enroll_to_baseline(
            visit_schedule_name=self.visit_schedule.name,
            schedule_name="schedule",
            gender=FEMALE,
        )

        for panel, entry_status in [
            (self.panel_one, REQUIRED),
            (self.panel_two, REQUIRED),
            (self.panel_three, NOT_REQUIRED),
            (self.panel_four, NOT_REQUIRED),
            (self.panel_five, NOT_REQUIRED),
            (self.panel_six, NOT_REQUIRED),
            (self.panel_seven, NOT_REQUIRED),
            (self.panel_eight, NOT_REQUIRED),
        ]:
            with self.subTest(panel=panel):
                obj = RequisitionMetadata.objects.get(
                    model="clinicedc_tests.subjectrequisition",
                    subject_identifier=subject_visit.subject_identifier,
                    visit_code=subject_visit.visit_code,
                    panel_name=panel.name,
                )
                self.assertEqual(obj.entry_status, entry_status)

        CrfOne.objects.create(subject_visit=subject_visit, f1="hello")

        for panel, entry_status in [
            (self.panel_one, REQUIRED),
            (self.panel_two, REQUIRED),
            (self.panel_three, NOT_REQUIRED),
            (self.panel_four, NOT_REQUIRED),
            (self.panel_five, NOT_REQUIRED),
            (self.panel_six, REQUIRED),
            (self.panel_seven, REQUIRED),
            (self.panel_eight, REQUIRED),
        ]:
            with self.subTest(panel=panel):
                obj = RequisitionMetadata.objects.get(
                    model="clinicedc_tests.subjectrequisition",
                    subject_identifier=subject_visit.subject_identifier,
                    visit_code=subject_visit.visit_code,
                    panel_name=panel.name,
                )
                self.assertEqual(obj.entry_status, entry_status)

    # TODO: fix
    @time_machine.travel(test_datetime)
    def test_keyed_instance_ignores_rules(self):
        """Asserts if instance exists, rule is ignored"""
        site_metadata_rules.registry = {}
        site_metadata_rules.register(RequisitionRuleGroup3)

        subject_visit = self.helper.enroll_to_baseline(
            visit_schedule_name=self.visit_schedule.name,
            schedule_name="schedule",
            gender=FEMALE,
        )

        # check default entry status
        metadata_obj = RequisitionMetadata.objects.get(
            model="clinicedc_tests.subjectrequisition",
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code,
            panel_name=self.panel_six.name,
        )
        self.assertEqual(metadata_obj.entry_status, NOT_REQUIRED)

        # create CRF that triggers rule to REQUIRED
        crf_one = CrfOne.objects.create(subject_visit=subject_visit, f1="hello")
        metadata_obj = RequisitionMetadata.objects.get(
            model="clinicedc_tests.subjectrequisition",
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code,
            panel_name=self.panel_six.name,
        )
        self.assertEqual(metadata_obj.entry_status, REQUIRED)

        # change CRF value, reverts to default status
        crf_one.f1 = "goodbye"
        crf_one.save()
        metadata_obj = RequisitionMetadata.objects.get(
            model="clinicedc_tests.subjectrequisition",
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code,
            panel_name=self.panel_six.name,
        )
        self.assertEqual(metadata_obj.entry_status, NOT_REQUIRED)

        # change CRF value, triggers REQUIRED
        crf_one.f1 = "hello"
        crf_one.save()
        metadata_obj = RequisitionMetadata.objects.get(
            model="clinicedc_tests.subjectrequisition",
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code,
            panel_name=self.panel_six.name,
        )
        self.assertEqual(metadata_obj.entry_status, REQUIRED)

        # KEY requisition
        SubjectRequisition.objects.create(subject_visit=subject_visit, panel=self.panel_six)
        metadata_obj = RequisitionMetadata.objects.get(
            model="clinicedc_tests.subjectrequisition",
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code,
            panel_name=self.panel_six.name,
        )
        self.assertEqual(metadata_obj.entry_status, KEYED)

        # change CRF value
        crf_one.f1 = "goodbye"
        crf_one.save()

        # assert KEYED value was not changed, rule was ignored
        metadata_obj = RequisitionMetadata.objects.get(
            model="clinicedc_tests.subjectrequisition",
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code,
            panel_name=self.panel_six.name,
        )
        self.assertEqual(metadata_obj.entry_status, KEYED)

    @time_machine.travel(test_datetime)
    def test_recovers_from_sequence_problem(self):
        """Asserts if instance exists, rule is ignored."""
        subject_visit = self.helper.enroll_to_baseline(
            visit_schedule_name=self.visit_schedule.name,
            schedule_name="schedule",
            gender=FEMALE,
        )
        site_metadata_rules.registry = {}
        site_metadata_rules.register(RequisitionRuleGroup3)
        # create CRF that triggers rule to REQUIRED
        crf_one = CrfOne.objects.create(subject_visit=subject_visit, f1="hello")
        metadata_obj = RequisitionMetadata.objects.get(
            model="clinicedc_tests.subjectrequisition",
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code,
            panel_name=self.panel_six.name,
        )
        self.assertEqual(metadata_obj.entry_status, REQUIRED)

        # KEY requisition
        SubjectRequisition.objects.create(subject_visit=subject_visit, panel=self.panel_six)
        metadata_obj = RequisitionMetadata.objects.get(
            model="clinicedc_tests.subjectrequisition",
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code,
            panel_name=self.panel_six.name,
        )
        self.assertEqual(metadata_obj.entry_status, KEYED)

        # mess up sequence
        metadata_obj.entry_status = NOT_REQUIRED
        metadata_obj.save()

        # resave to trigger rules
        crf_one.save()

        # assert KEYED value was not changed, rule was ignored
        metadata_obj = RequisitionMetadata.objects.get(
            model="clinicedc_tests.subjectrequisition",
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code,
            panel_name=self.panel_six.name,
        )
        self.assertEqual(metadata_obj.entry_status, KEYED)

    @time_machine.travel(test_datetime)
    def test_recovers_from_missing_metadata(self):
        site_metadata_rules.registry = {}
        site_metadata_rules.register(RequisitionRuleGroup3)
        subject_visit = self.helper.enroll_to_baseline(
            visit_schedule_name=self.visit_schedule.name,
            schedule_name="schedule",
            gender=FEMALE,
        )
        try:
            RequisitionMetadata.objects.get(
                model="clinicedc_tests.subjectrequisition",
                subject_identifier=subject_visit.subject_identifier,
                visit_code=subject_visit.visit_code,
                panel_name=self.panel_six.name,
                entry_status=NOT_REQUIRED,
            )
        except ObjectDoesNotExist:
            self.fail("RequisitionMetadata unexepectedly does not exist")

        # create CRF that triggers rule to panel_six = REQUIRED
        crf_one = CrfOne.objects.create(subject_visit=subject_visit, f1="hello")
        metadata_obj = RequisitionMetadata.objects.get(
            model="clinicedc_tests.subjectrequisition",
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code,
            panel_name=self.panel_six.name,
        )
        self.assertEqual(metadata_obj.entry_status, REQUIRED)

        # KEY requisition
        SubjectRequisition.objects.create(subject_visit=subject_visit, panel=self.panel_six)
        metadata_obj = RequisitionMetadata.objects.get(
            model="clinicedc_tests.subjectrequisition",
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code,
            panel_name=self.panel_six.name,
        )
        self.assertEqual(metadata_obj.entry_status, KEYED)

        # delete metadata
        metadata_obj.delete()

        # resave to trigger rules
        crf_one.save()

        # assert KEYED value was not changed, rule was ignored
        metadata_obj = RequisitionMetadata.objects.get(
            model="clinicedc_tests.subjectrequisition",
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code,
            panel_name=self.panel_six.name,
        )
        self.assertEqual(metadata_obj.entry_status, KEYED)
