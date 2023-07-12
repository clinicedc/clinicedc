from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from edc_constants.constants import FEMALE, MALE
from edc_facility.import_holidays import import_holidays
from edc_lab.models import Panel
from edc_reference import site_reference_configs
from edc_reference.models import Reference
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from faker import Faker

from ...constants import KEYED, NOT_REQUIRED, REQUIRED
from ...metadata_rules import (
    P,
    RequisitionRule,
    RequisitionRuleGroup,
    RequisitionRuleGroupMetaOptionsError,
    site_metadata_rules,
)
from ...models import RequisitionMetadata
from ..models import (
    Appointment,
    CrfOne,
    SubjectConsent,
    SubjectRequisition,
    SubjectVisit,
)
from ..reference_configs import register_to_site_reference_configs
from ..visit_schedule import visit_schedule

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
        app_label = "edc_metadata"
        source_model = "edc_metadata.crfone"
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
        app_label = "edc_metadata"
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
        app_label = "edc_metadata"
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
        app_label = "edc_metadata"
        source_model = "crfone"
        requisition_model = "subjectrequisition"


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

        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)

        register_to_site_reference_configs()
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "edc_metadata.subjectvisit"}
        )
        _, self.schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_metadata.onschedule"
        )
        site_metadata_rules.registry = {}

    def enroll(self, gender=None):
        """Returns a subject visit model after enrolling a
        subject of the given gender.
        """
        subject_identifier = fake.credit_card_number()
        subject_consent = SubjectConsent.objects.create(
            subject_identifier=subject_identifier,
            consent_datetime=get_utcnow(),
            gender=gender,
        )
        self.schedule.put_on_schedule(
            subject_identifier=subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )
        self.appointment = Appointment.objects.get(
            subject_identifier=subject_identifier,
            visit_code=self.schedule.visits.first.code,
        )
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment,
            reason=SCHEDULED,
            subject_identifier=subject_identifier,
        )
        return subject_visit

    def test_rule_male(self):
        subject_visit = self.enroll(gender=MALE)
        rule_results, _ = MyRequisitionRuleGroup().evaluate_rules(related_visit=subject_visit)
        for panel in [self.panel_one, self.panel_two]:
            with self.subTest(panel=panel):
                key = "edc_metadata.subjectrequisition"
                for rule_result in rule_results["MyRequisitionRuleGroup.male"][key]:
                    self.assertEqual(rule_result.entry_status, REQUIRED)
                for rule_result in rule_results["MyRequisitionRuleGroup.female"][key]:
                    self.assertEqual(rule_result.entry_status, NOT_REQUIRED)

    def test_rule_female(self):
        subject_visit = self.enroll(gender=FEMALE)
        rule_results, _ = MyRequisitionRuleGroup().evaluate_rules(related_visit=subject_visit)
        for panel in [self.panel_one, self.panel_two]:
            with self.subTest(panel=panel):
                key = "edc_metadata.subjectrequisition"
                for rule_result in rule_results["MyRequisitionRuleGroup.female"].get(key):
                    self.assertEqual(rule_result.entry_status, REQUIRED)
                for rule_result in rule_results["MyRequisitionRuleGroup.male"].get(key):
                    self.assertEqual(rule_result.entry_status, NOT_REQUIRED)

    def test_source_panel_required_raises(self):
        try:

            class BadRequisitionRuleGroup(BaseRequisitionRuleGroup):
                class Meta:
                    app_label = "edc_metadata"
                    source_model = "subjectrequisition"
                    requisition_model = "subjectrequisition"

        except RequisitionRuleGroupMetaOptionsError as e:
            self.assertEqual(e.code, "source_panel_expected")
        else:
            self.fail(
                "RequisitionRuleGroupMetaOptionsError "
                f"not raised for {BadRequisitionRuleGroup}"
            )

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
                    app_label = "edc_metadata"
                    source_model = "crf_one"
                    requisition_model = "subjectrequisition"

        except RequisitionRuleGroupMetaOptionsError as e:
            self.assertEqual(e.code, "source_panel_not_expected")
        else:
            self.fail(
                "RequisitionRuleGroupMetaOptionsError not "
                f"raised for {BadRequisitionRuleGroup}"
            )

    def test_rule_male_with_source_model_as_requisition(self):
        subject_visit = self.enroll(gender=MALE)
        rule_results, _ = RequisitionRuleGroup2().evaluate_rules(related_visit=subject_visit)
        for panel_name in ["one", "two"]:
            with self.subTest(panel_name=panel_name):
                key = "edc_metadata.subjectrequisition"
                for rule_result in rule_results["RequisitionRuleGroup2.male"][key]:
                    self.assertEqual(rule_result.entry_status, REQUIRED)
                for rule_result in rule_results["RequisitionRuleGroup2.female"][key]:
                    self.assertEqual(rule_result.entry_status, NOT_REQUIRED)

    def test_metadata_for_rule_male_with_source_model_as_requisition1(self):
        """RequisitionRuleGroup2"""
        site_metadata_rules.registry = {}
        site_metadata_rules.register(RequisitionRuleGroup2)
        subject_visit = self.enroll(gender=MALE)
        SubjectRequisition.objects.create(subject_visit=subject_visit, panel=self.panel_five)
        for panel_name in ["one", "two"]:
            with self.subTest(panel_name=panel_name):
                obj = RequisitionMetadata.objects.get(
                    model="edc_metadata.subjectrequisition",
                    subject_identifier=subject_visit.subject_identifier,
                    visit_code=subject_visit.visit_code,
                    panel_name=panel_name,
                )
                self.assertEqual(obj.entry_status, REQUIRED)

    def test_metadata_for_rule_male_with_source_model_as_requisition2(self):
        subject_visit = self.enroll(gender=MALE)
        site_metadata_rules.registry = {}
        site_metadata_rules.register(RequisitionRuleGroup2)
        SubjectRequisition.objects.create(subject_visit=subject_visit, panel=self.panel_five)
        for panel_name in ["three", "four"]:
            with self.subTest(panel_name=panel_name):
                obj = RequisitionMetadata.objects.get(
                    model="edc_metadata.subjectrequisition",
                    subject_identifier=subject_visit.subject_identifier,
                    visit_code=subject_visit.visit_code,
                    panel_name=panel_name,
                )
                self.assertEqual(obj.entry_status, NOT_REQUIRED)

    def test_metadata_for_rule_female_with_source_model_as_requisition1(self):
        subject_visit = self.enroll(gender=FEMALE)
        site_metadata_rules.registry = {}
        site_metadata_rules.register(RequisitionRuleGroup2)
        Reference.objects.create(
            visit_schedule_name=subject_visit.visit_schedule_name,
            schedule_name=subject_visit.schedule_name,
            visit_code=subject_visit.visit_code,
            timepoint=subject_visit.timepoint,
            identifier=subject_visit.subject_identifier,
            report_datetime=subject_visit.report_datetime,
            field_name="panel",
            value_uuid=self.panel_five.id,
        )
        SubjectRequisition.objects.create(subject_visit=subject_visit, panel=self.panel_five)
        for panel in [self.panel_three, self.panel_four]:
            with self.subTest(panel=panel):
                obj = RequisitionMetadata.objects.get(
                    model="edc_metadata.subjectrequisition",
                    subject_identifier=subject_visit.subject_identifier,
                    visit_code=subject_visit.visit_code,
                    panel_name=panel.name,
                )
                self.assertEqual(obj.entry_status, REQUIRED)

    def test_metadata_for_rule_female_with_source_model_as_requisition2(self):
        subject_visit = self.enroll(gender=FEMALE)
        site_metadata_rules.registry = {}
        site_metadata_rules.register(RequisitionRuleGroup2)
        SubjectRequisition.objects.create(subject_visit=subject_visit, panel=self.panel_five)
        for panel in [self.panel_one, self.panel_two]:
            with self.subTest(panel=panel):
                obj = RequisitionMetadata.objects.get(
                    model="edc_metadata.subjectrequisition",
                    subject_identifier=subject_visit.subject_identifier,
                    visit_code=subject_visit.visit_code,
                    panel_name=panel.name,
                )
                self.assertEqual(obj.entry_status, NOT_REQUIRED)

    def test_metadata_requisition(self):
        site_metadata_rules.registry = {}
        site_metadata_rules.register(RequisitionRuleGroup3)

        subject_visit = self.enroll(gender=FEMALE)

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
                    model="edc_metadata.subjectrequisition",
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
                    model="edc_metadata.subjectrequisition",
                    subject_identifier=subject_visit.subject_identifier,
                    visit_code=subject_visit.visit_code,
                    panel_name=panel.name,
                )
                self.assertEqual(obj.entry_status, entry_status)

    # TODO: fix
    def test_keyed_instance_ignores_rules(self):
        """Asserts if instance exists, rule is ignored"""
        site_metadata_rules.registry = {}
        site_metadata_rules.register(RequisitionRuleGroup3)

        subject_visit = self.enroll(gender=FEMALE)

        Reference.objects.create(
            visit_schedule_name=subject_visit.visit_schedule_name,
            schedule_name=subject_visit.schedule_name,
            visit_code=subject_visit.visit_code,
            timepoint=subject_visit.timepoint,
            identifier=subject_visit.subject_identifier,
            report_datetime=subject_visit.report_datetime,
            field_name="panel",
            value_uuid=self.panel_five.id,
        )

        # check default entry status
        metadata_obj = RequisitionMetadata.objects.get(
            model="edc_metadata.subjectrequisition",
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code,
            panel_name=self.panel_six.name,
        )
        self.assertEqual(metadata_obj.entry_status, NOT_REQUIRED)

        # create CRF that triggers rule to REQUIRED
        crf_one = CrfOne.objects.create(subject_visit=subject_visit, f1="hello")
        metadata_obj = RequisitionMetadata.objects.get(
            model="edc_metadata.subjectrequisition",
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code,
            panel_name=self.panel_six.name,
        )
        self.assertEqual(metadata_obj.entry_status, REQUIRED)

        # change CRF value, reverts to default status
        crf_one.f1 = "goodbye"
        crf_one.save()
        metadata_obj = RequisitionMetadata.objects.get(
            model="edc_metadata.subjectrequisition",
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code,
            panel_name=self.panel_six.name,
        )
        self.assertEqual(metadata_obj.entry_status, NOT_REQUIRED)

        # change CRF value, triggers REQUIRED
        crf_one.f1 = "hello"
        crf_one.save()
        metadata_obj = RequisitionMetadata.objects.get(
            model="edc_metadata.subjectrequisition",
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code,
            panel_name=self.panel_six.name,
        )
        self.assertEqual(metadata_obj.entry_status, REQUIRED)

        # KEY requisition
        SubjectRequisition.objects.create(subject_visit=subject_visit, panel=self.panel_six)
        metadata_obj = RequisitionMetadata.objects.get(
            model="edc_metadata.subjectrequisition",
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
            model="edc_metadata.subjectrequisition",
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code,
            panel_name=self.panel_six.name,
        )
        self.assertEqual(metadata_obj.entry_status, KEYED)

    def test_recovers_from_sequence_problem(self):
        """Asserts if instance exists, rule is ignored."""
        subject_visit = self.enroll(gender=FEMALE)
        site_metadata_rules.registry = {}
        site_metadata_rules.register(RequisitionRuleGroup3)
        Reference.objects.create(
            visit_schedule_name=subject_visit.visit_schedule_name,
            schedule_name=subject_visit.schedule_name,
            visit_code=subject_visit.visit_code,
            timepoint=subject_visit.timepoint,
            identifier=subject_visit.subject_identifier,
            report_datetime=subject_visit.report_datetime,
            field_name="panel",
            value_uuid=self.panel_five.id,
        )

        # create CRF that triggers rule to REQUIRED
        crf_one = CrfOne.objects.create(subject_visit=subject_visit, f1="hello")
        metadata_obj = RequisitionMetadata.objects.get(
            model="edc_metadata.subjectrequisition",
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code,
            panel_name=self.panel_six.name,
        )
        self.assertEqual(metadata_obj.entry_status, REQUIRED)

        # KEY requisition
        SubjectRequisition.objects.create(subject_visit=subject_visit, panel=self.panel_six)
        metadata_obj = RequisitionMetadata.objects.get(
            model="edc_metadata.subjectrequisition",
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
            model="edc_metadata.subjectrequisition",
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code,
            panel_name=self.panel_six.name,
        )
        self.assertEqual(metadata_obj.entry_status, KEYED)

    def test_recovers_from_missing_metadata(self):
        site_metadata_rules.registry = {}
        site_metadata_rules.register(RequisitionRuleGroup3)
        subject_visit = self.enroll(gender=FEMALE)
        try:
            RequisitionMetadata.objects.get(
                model="edc_metadata.subjectrequisition",
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
            model="edc_metadata.subjectrequisition",
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code,
            panel_name=self.panel_six.name,
        )
        self.assertEqual(metadata_obj.entry_status, REQUIRED)

        # KEY requisition
        SubjectRequisition.objects.create(subject_visit=subject_visit, panel=self.panel_six)
        metadata_obj = RequisitionMetadata.objects.get(
            model="edc_metadata.subjectrequisition",
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
            model="edc_metadata.subjectrequisition",
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code,
            panel_name=self.panel_six.name,
        )
        self.assertEqual(metadata_obj.entry_status, KEYED)
