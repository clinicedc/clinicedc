from collections import OrderedDict
from django.test import TestCase, tag
from faker import Faker

from edc_constants.constants import MALE, FEMALE
from edc_reference.models import Reference
from edc_registration.models import RegisteredSubject
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from ..constants import NOT_REQUIRED, REQUIRED
from ..models import RequisitionMetadata
from ..rules import RequisitionRuleGroup, RequisitionRule, P, site_metadata_rules
from ..rules import RequisitionMetadataError, RequisitionRuleGroupMetaOptionsError
from .metadata_rules import register_to_site_reference_configs
from .models import Appointment, SubjectVisit, Enrollment, SubjectRequisition
from .visit_schedule import visit_schedule

fake = Faker()


class RequisitionPanel:
    def __init__(self, name):
        self.name = name


panel_one = RequisitionPanel('one')
panel_two = RequisitionPanel('two')
panel_three = RequisitionPanel('three')
panel_four = RequisitionPanel('four')
panel_five = RequisitionPanel('five')
panel_six = RequisitionPanel('six')


class BadPanelsRequisitionRuleGroup(RequisitionRuleGroup):
    """Specifies invalid panel names.
    """

    rule = RequisitionRule(
        predicate=P('gender', 'eq', MALE),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_panels=['blah1', 'blah2'])

    class Meta:
        app_label = 'edc_metadata'
        source_model = 'edc_metadata.crfone'
        requisition_model = 'subjectrequisition'


class RequisitionRuleGroup2(RequisitionRuleGroup):
    """A rule group where source model is a requisition.
    """

    male = RequisitionRule(
        predicate=P('gender', 'eq', MALE),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        source_panel=panel_five,
        target_panels=[panel_one, panel_two])

    female = RequisitionRule(
        predicate=P('gender', 'eq', FEMALE),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        source_panel=panel_six,
        target_panels=[panel_three, panel_four])

    class Meta:
        app_label = 'edc_metadata'
        source_model = 'subjectrequisition'
        requisition_model = 'subjectrequisition'


class BaseRequisitionRuleGroup(RequisitionRuleGroup):

    male = RequisitionRule(
        predicate=P('gender', 'eq', MALE),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_panels=[panel_one, panel_two])

    female = RequisitionRule(
        predicate=P('gender', 'eq', FEMALE),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_panels=[panel_three, panel_four])

    class Meta:
        abstract = True


class MyRequisitionRuleGroup(BaseRequisitionRuleGroup):
    """A rule group where source model is NOT a requisition.
    """

    class Meta:
        app_label = 'edc_metadata'
        source_model = 'crfone'
        requisition_model = 'subjectrequisition'


class TestRequisitionRuleGroup(TestCase):

    def setUp(self):

        register_to_site_reference_configs()
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)

        self.schedule = site_visit_schedules.get_schedule(
            visit_schedule_name='visit_schedule',
            schedule_name='schedule')

        site_metadata_rules.registry = OrderedDict()
        # site_metadata_rules.register(rule_group_cls=CrfRuleGroupGender)

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

    def test_rule_bad_panel_names(self):
        subject_visit = self.enroll(gender=MALE)
        self.assertRaises(
            RequisitionMetadataError,
            BadPanelsRequisitionRuleGroup().evaluate_rules, visit=subject_visit)

    def test_rule_male(self):
        subject_visit = self.enroll(gender=MALE)
        rule_results, _ = MyRequisitionRuleGroup().evaluate_rules(visit=subject_visit)
        for panel_name in ['one', 'two']:
            with self.subTest(panel_name=panel_name):
                key = f'edc_metadata.subjectrequisition'
                for rule_result in rule_results[
                        'MyRequisitionRuleGroup.male'][key]:
                    self.assertEqual(rule_result.entry_status, REQUIRED)
                for rule_result in rule_results[
                        'MyRequisitionRuleGroup.female'][key]:
                    self.assertEqual(rule_result.entry_status, NOT_REQUIRED)

    def test_rule_female(self):
        subject_visit = self.enroll(gender=FEMALE)
        rule_results, _ = MyRequisitionRuleGroup().evaluate_rules(visit=subject_visit)
        for panel_name in ['one', 'two']:
            with self.subTest(panel_name=panel_name):
                key = f'edc_metadata.subjectrequisition'
                for rule_result in rule_results[
                        'MyRequisitionRuleGroup.female'].get(key):
                    self.assertEqual(rule_result.entry_status, REQUIRED)
                for rule_result in rule_results[
                        'MyRequisitionRuleGroup.male'].get(key):
                    self.assertEqual(rule_result.entry_status, NOT_REQUIRED)

    def test_source_panel_required_raises(self):
        try:
            class BadRequisitionRuleGroup(BaseRequisitionRuleGroup):

                class Meta:
                    app_label = 'edc_metadata'
                    source_model = 'subjectrequisition'
                    requisition_model = 'subjectrequisition'
        except RequisitionRuleGroupMetaOptionsError:
            pass
        else:
            self.fail('RequisitionRuleGroupMetaOptionsError not raised')

    def test_source_panel_not_required_raises(self):
        try:
            class BadRequisitionRuleGroup(RequisitionRuleGroup):

                male = RequisitionRule(
                    predicate=P('gender', 'eq', MALE),
                    consequence=REQUIRED,
                    alternative=NOT_REQUIRED,
                    source_panel=panel_one,
                    target_panels=[panel_one, panel_two])

                female = RequisitionRule(
                    predicate=P('gender', 'eq', FEMALE),
                    consequence=REQUIRED,
                    alternative=NOT_REQUIRED,
                    source_panel=panel_two,
                    target_panels=[panel_three, panel_four])

                class Meta:
                    app_label = 'edc_metadata'
                    source_model = 'crf_one'
                    requisition_model = 'subjectrequisition'
        except RequisitionRuleGroupMetaOptionsError:
            pass
        else:
            self.fail('RequisitionRuleGroupMetaOptionsError not raised')

    def test_rule_male_with_source_model_as_requisition(self):
        subject_visit = self.enroll(gender=MALE)
        rule_results, _ = RequisitionRuleGroup2().evaluate_rules(visit=subject_visit)
        for panel_name in ['one', 'two']:
            with self.subTest(panel_name=panel_name):
                key = f'edc_metadata.subjectrequisition'
                for rule_result in rule_results[
                        'RequisitionRuleGroup2.male'][key]:
                    self.assertEqual(rule_result.entry_status, REQUIRED)
                for rule_result in rule_results[
                        'RequisitionRuleGroup2.female'][key]:
                    self.assertEqual(rule_result.entry_status, NOT_REQUIRED)

    def test_metadata_for_rule_male_with_source_model_as_requisition1(self):
        subject_visit = self.enroll(gender=MALE)
        site_metadata_rules.registry = OrderedDict()
        site_metadata_rules.register(RequisitionRuleGroup2)
        SubjectRequisition.objects.create(
            subject_visit=subject_visit, panel_name=panel_five.name)
        for panel_name in ['one', 'two']:
            with self.subTest(panel_name=panel_name):
                obj = RequisitionMetadata.objects.get(
                    model='edc_metadata.subjectrequisition',
                    subject_identifier=subject_visit.subject_identifier,
                    visit_code=subject_visit.visit_code,
                    panel_name=panel_name)
                self.assertEqual(obj.entry_status, REQUIRED)

    def test_metadata_for_rule_male_with_source_model_as_requisition2(self):
        subject_visit = self.enroll(gender=MALE)
        site_metadata_rules.registry = OrderedDict()
        site_metadata_rules.register(RequisitionRuleGroup2)
        SubjectRequisition.objects.create(
            subject_visit=subject_visit, panel_name=panel_five.name)
        for panel_name in ['three', 'four']:
            with self.subTest(panel_name=panel_name):
                obj = RequisitionMetadata.objects.get(
                    model='edc_metadata.subjectrequisition',
                    subject_identifier=subject_visit.subject_identifier,
                    visit_code=subject_visit.visit_code,
                    panel_name=panel_name)
                self.assertEqual(obj.entry_status, NOT_REQUIRED)

    def test_metadata_for_rule_female_with_source_model_as_requisition1(self):
        subject_visit = self.enroll(gender=FEMALE)
        site_metadata_rules.registry = OrderedDict()
        site_metadata_rules.register(RequisitionRuleGroup2)
        Reference.objects.create(
            timepoint=subject_visit.visit_code,
            identifier=subject_visit.subject_identifier,
            report_datetime=subject_visit.report_datetime,
            field_name='panel_name',
            value_str=panel_five.name)
        SubjectRequisition.objects.create(
            subject_visit=subject_visit, panel_name=panel_five.name)
        for panel_name in ['three', 'four']:
            with self.subTest(panel_name=panel_name):
                obj = RequisitionMetadata.objects.get(
                    model='edc_metadata.subjectrequisition',
                    subject_identifier=subject_visit.subject_identifier,
                    visit_code=subject_visit.visit_code,
                    panel_name=panel_name)
                self.assertEqual(obj.entry_status, REQUIRED)

    def test_metadata_for_rule_female_with_source_model_as_requisition2(self):
        subject_visit = self.enroll(gender=FEMALE)
        site_metadata_rules.registry = OrderedDict()
        site_metadata_rules.register(RequisitionRuleGroup2)
        SubjectRequisition.objects.create(
            subject_visit=subject_visit, panel_name=panel_five.name)
        for panel_name in ['one', 'two']:
            with self.subTest(panel_name=panel_name):
                obj = RequisitionMetadata.objects.get(
                    model='edc_metadata.subjectrequisition',
                    subject_identifier=subject_visit.subject_identifier,
                    visit_code=subject_visit.visit_code,
                    panel_name=panel_name)
                self.assertEqual(obj.entry_status, NOT_REQUIRED)
