from collections import OrderedDict
from django.test import TestCase, tag
from faker import Faker

from edc_constants.constants import MALE, FEMALE
from edc_registration.models import RegisteredSubject
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from ..constants import NOT_REQUIRED, REQUIRED
from ..models import RequisitionMetadata
from ..rules import RequisitionRuleGroup, RequisitionRule, P, site_metadata_rules
from ..rules import RequisitionMetadataError
from .models import Appointment, SubjectVisit, Enrollment, CrfOne
from .visit_schedule import visit_schedule

fake = Faker()


class RequisitionPanel:
    def __init__(self, name):
        self.name = name


panel_one = RequisitionPanel('one')
panel_two = RequisitionPanel('two')
panel_three = RequisitionPanel('three')
panel_four = RequisitionPanel('four')


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


class MyRequisitionRuleGroup1(BaseRequisitionRuleGroup):

    class Meta:
        app_label = 'edc_metadata'
        source_model = 'crfone'
        requisition_model = 'subjectrequisition'


class MyRequisitionRuleGroup2(BaseRequisitionRuleGroup):

    class Meta:
        app_label = 'edc_metadata'
        source_model = 'subjectrequisition'
        requisition_model = 'subjectrequisition'


class TestRequisitionRuleGroup(TestCase):

    def setUp(self):

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

    @tag('1')
    def test_rule_bad_panel_names(self):
        subject_visit = self.enroll(gender=MALE)
        self.assertRaises(
            RequisitionMetadataError,
            BadPanelsRequisitionRuleGroup().evaluate_rules, visit=subject_visit)

    @tag('1')
    def test_rule_male(self):
        subject_visit = self.enroll(gender=MALE)
        rule_results, _ = MyRequisitionRuleGroup1().evaluate_rules(visit=subject_visit)
        for panel_name in ['one', 'two']:
            with self.subTest(panel_name=panel_name):
                key = f'edc_metadata.subjectrequisition'
                for rule_result in rule_results[
                        'MyRequisitionRuleGroup1.male'][key]:
                    self.assertEqual(rule_result.entry_status, REQUIRED)
                for rule_result in rule_results[
                        'MyRequisitionRuleGroup1.female'][key]:
                    self.assertEqual(rule_result.entry_status, NOT_REQUIRED)

    @tag('1')
    def test_rule_female(self):
        subject_visit = self.enroll(gender=FEMALE)
        rule_results, _ = MyRequisitionRuleGroup1().evaluate_rules(visit=subject_visit)
        for panel_name in ['one', 'two']:
            with self.subTest(panel_name=panel_name):
                key = f'edc_metadata.subjectrequisition'
                for rule_result in rule_results[
                        'MyRequisitionRuleGroup1.female'].get(key):
                    self.assertEqual(rule_result.entry_status, REQUIRED)
                for rule_result in rule_results[
                        'MyRequisitionRuleGroup1.male'].get(key):
                    self.assertEqual(rule_result.entry_status, NOT_REQUIRED)
