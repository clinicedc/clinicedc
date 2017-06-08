from dateutil.relativedelta import relativedelta

from django.apps import apps as django_apps
from django.test import TestCase, tag
from model_mommy import mommy

from edc_base.utils import get_utcnow
from edc_constants.constants import MALE, FEMALE
# from edc_example.models import (
#     Appointment, CrfOne, CrfTwo, CrfThree, CrfFive, CrfFour, Enrollment)
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ..constants import NOT_REQUIRED, REQUIRED, KEYED
from ..models import CrfMetadata

from ..rules.crf_rule import CrfRule
from ..rules.exceptions import RuleError
from ..rules.logic import Logic
from ..rules.predicate import P, PF
from ..rules.rule_group import RuleGroup
from ..rules.site_rule_groups import site_rule_groups, AlreadyRegistered

edc_registration_app_config = django_apps.get_app_config('edc_registration')


class MetadataRulesTests(TestCase):

    def setUp(self):
        django_apps.app_configs['edc_metadata'].metadata_rules_enabled = True
        visit_schedule = site_visit_schedules.get_visit_schedule(
            Enrollment._meta.visit_schedule_name)
        self.schedule = visit_schedule.get_schedule(
            Enrollment._meta.label_lower)
        self.first_visit = self.schedule.get_first_visit()
        self.panel_name = self.first_visit.requisitions[0].panel.name

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

    def test_example_rules_run_if_male(self):
        subject_consent = mommy.make_recipe(
            'edc_example.subjectconsent',
            subject_identifier='123456789-0', gender=MALE)
        enrollment = mommy.make_recipe(
            'edc_example.enrollment',
            subject_identifier=subject_consent.subject_identifier,
            schedule_name='schedule1')
        appointment = Appointment.objects.get(
            subject_identifier=enrollment.subject_identifier,
            visit_code=self.first_visit.code)
        subject_visit = mommy.make_recipe(
            'edc_example.subjectvisit',
            appointment=appointment)
        self.assertEqual(
            CrfMetadata.objects.get(
                model=CrfTwo._meta.label_lower,
                subject_identifier=subject_visit.subject_identifier,
                visit_code=self.first_visit.code
            ).entry_status, NOT_REQUIRED)
        self.assertEqual(
            CrfMetadata.objects.get(
                model=CrfThree._meta.label_lower,
                subject_identifier=subject_visit.subject_identifier,
                visit_code=self.first_visit.code
            ).entry_status, NOT_REQUIRED)
        self.assertEqual(
            CrfMetadata.objects.get(
                model=CrfFour._meta.label_lower,
                subject_identifier=subject_visit.subject_identifier,
                visit_code=self.first_visit.code
            ).entry_status, REQUIRED)
        self.assertEqual(
            CrfMetadata.objects.get(
                model=CrfFive._meta.label_lower,
                subject_identifier=subject_visit.subject_identifier,
                visit_code=self.first_visit.code
            ).entry_status, REQUIRED)

    def test_example_rules_run_if_female(self):
        subject_consent = mommy.make_recipe(
            'edc_example.subjectconsent',
            subject_identifier='123456789-0', gender=FEMALE)
        enrollment = mommy.make_recipe(
            'edc_example.enrollment',
            subject_identifier=subject_consent.subject_identifier,
            schedule_name='schedule1')
        appointment = Appointment.objects.get(
            subject_identifier=enrollment.subject_identifier,
            visit_code=self.first_visit.code)
        subject_visit = mommy.make_recipe(
            'edc_example.subjectvisit', appointment=appointment)
        self.assertEqual(
            CrfMetadata.objects.get(
                model=CrfTwo._meta.label_lower,
                subject_identifier=subject_visit.subject_identifier,
                visit_code=self.first_visit.code
            ).entry_status, REQUIRED)
        self.assertEqual(
            CrfMetadata.objects.get(
                model=CrfThree._meta.label_lower,
                subject_identifier=subject_visit.subject_identifier,
                visit_code=self.first_visit.code
            ).entry_status, REQUIRED)
        self.assertEqual(
            CrfMetadata.objects.get(
                model=CrfFour._meta.label_lower,
                subject_identifier=subject_visit.subject_identifier,
                visit_code=self.first_visit.code
            ).entry_status, NOT_REQUIRED)
        self.assertEqual(
            CrfMetadata.objects.get(
                model=CrfFive._meta.label_lower,
                subject_identifier=subject_visit.subject_identifier,
                visit_code=self.first_visit.code
            ).entry_status, NOT_REQUIRED)

    def test_register_twice_raises(self):

        class ExampleCrfRuleGroup(RuleGroup):

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
                app_label = 'edc_example'

        self.assertRaises(AlreadyRegistered,
                          site_rule_groups.register, ExampleCrfRuleGroup)

    def test_example2(self):
        """Asserts CrfTwo is REQUIRED if f1==\'car\' as specified
        by edc_example.rule_groups.ExampleRuleGroup2."""
        subject_consent = mommy.make_recipe(
            'edc_example.subjectconsent',
            subject_identifier='123456789-0', gender=MALE)
        enrollment = mommy.make_recipe(
            'edc_example.enrollment',
            subject_identifier=subject_consent.subject_identifier,
            schedule_name='schedule1')
        appointment = Appointment.objects.get(
            subject_identifier=enrollment.subject_identifier,
            visit_code=self.first_visit.code)
        subject_visit = mommy.make_recipe(
            'edc_example.subjectvisit', appointment=appointment)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfTwo._meta.label_lower).entry_status, NOT_REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfThree._meta.label_lower).entry_status, NOT_REQUIRED)
        CrfOne.objects.create(subject_visit=subject_visit, f1='car')
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfTwo._meta.label_lower).entry_status, REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfThree._meta.label_lower).entry_status, NOT_REQUIRED)

    def test_example3(self):
        """Asserts CrfThree is REQUIRED if f1==\'bicycle\' as specified
        by edc_example.rule_groups.ExampleRuleGroup2."""
        subject_consent = mommy.make_recipe(
            'edc_example.subjectconsent',
            subject_identifier='123456789-0', gender=MALE)
        enrollment = mommy.make_recipe(
            'edc_example.enrollment',
            subject_identifier=subject_consent.subject_identifier,
            schedule_name='schedule1')
        appointment = Appointment.objects.get(
            subject_identifier=enrollment.subject_identifier,
            visit_code=self.first_visit.code)
        subject_visit = mommy.make_recipe(
            'edc_example.subjectvisit', appointment=appointment)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfTwo._meta.label_lower).entry_status, NOT_REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfThree._meta.label_lower).entry_status, NOT_REQUIRED)
        CrfOne.objects.create(subject_visit=subject_visit, f1='bicycle')
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfTwo._meta.label_lower).entry_status, NOT_REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfThree._meta.label_lower).entry_status, REQUIRED)

    def test_example4(self):
        """Asserts CrfThree is REQUIRED if f1==\'bicycle\' but then not when f1 is changed to \'car\' as specified
        by edc_example.rule_groups.ExampleRuleGroup2."""
        subject_consent = mommy.make_recipe(
            'edc_example.subjectconsent',
            subject_identifier='123456789-0', gender=MALE)
        enrollment = mommy.make_recipe(
            'edc_example.enrollment',
            subject_identifier=subject_consent.subject_identifier,
            schedule_name='schedule1')
        appointment = Appointment.objects.get(
            subject_identifier=enrollment.subject_identifier,
            visit_code=self.first_visit.code)
        subject_visit = mommy.make_recipe(
            'edc_example.subjectvisit', appointment=appointment)
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
        crf_one.f1 = 'car'
        crf_one.save()
        self.assertEqual(
            CrfMetadata.objects.get(
                model=CrfTwo._meta.label_lower,
                subject_identifier=subject_visit.subject_identifier,
                visit_code=self.first_visit.code
            ).entry_status, REQUIRED)
        self.assertEqual(
            CrfMetadata.objects.get(
                model=CrfThree._meta.label_lower,
                subject_identifier=subject_visit.subject_identifier,
                visit_code=self.first_visit.code
            ).entry_status, NOT_REQUIRED)

    def test_example5(self):
        """Asserts same as above for edc_example.rule_groups.ExampleRuleGroup2 but add
        a second visit and CrfOne."""
        subject_consent = mommy.make_recipe(
            'edc_example.subjectconsent',
            subject_identifier='123456789-0', gender=MALE)
        enrollment = mommy.make_recipe(
            'edc_example.enrollment',
            subject_identifier=subject_consent.subject_identifier,
            schedule_name='schedule1')
        appointment = Appointment.objects.get(
            subject_identifier=enrollment.subject_identifier,
            visit_code=self.first_visit.code)
        subject_visit1 = mommy.make_recipe(
            'edc_example.subjectvisit', appointment=appointment,
            report_datetime=get_utcnow() - relativedelta(days=5))
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfTwo._meta.label_lower).entry_status, NOT_REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfThree._meta.label_lower).entry_status, NOT_REQUIRED)
        CrfOne.objects.create(subject_visit=subject_visit1, f1='bicycle')
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfTwo._meta.label_lower).entry_status, NOT_REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfThree._meta.label_lower).entry_status, REQUIRED)
        next_visit = self.schedule.get_next_visit(self.first_visit.code)
        appointment = Appointment.objects.get(
            subject_identifier=enrollment.subject_identifier,
            visit_code=next_visit.code)
        subject_visit2 = mommy.make_recipe(
            'edc_example.subjectvisit', appointment=appointment)
        CrfOne.objects.create(subject_visit=subject_visit2, f1='car')
        self.assertEqual(
            CrfMetadata.objects.get(
                model=CrfTwo._meta.label_lower,
                subject_identifier=subject_visit1.subject_identifier,
                visit_code=self.first_visit.code
            ).entry_status, NOT_REQUIRED)
        self.assertEqual(
            CrfMetadata.objects.get(
                model=CrfThree._meta.label_lower,
                subject_identifier=subject_visit1.subject_identifier,
                visit_code=self.first_visit.code
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
        subject_consent = mommy.make_recipe(
            'edc_example.subjectconsent',
            subject_identifier='123456789-0', gender=MALE)
        enrollment = mommy.make_recipe(
            'edc_example.enrollment',
            subject_identifier=subject_consent.subject_identifier,
            schedule_name='schedule1')
        appointment = Appointment.objects.get(
            subject_identifier=enrollment.subject_identifier,
            visit_code=self.first_visit.code)
        subject_visit = mommy.make_recipe(
            'edc_example.subjectvisit', appointment=appointment)
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
        subject_visit.save()
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfTwo._meta.label_lower).entry_status, NOT_REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfThree._meta.label_lower).entry_status, REQUIRED)

    def test_example7(self):
        """Asserts if instance exists, rule is ignored."""
        subject_consent = mommy.make_recipe(
            'edc_example.subjectconsent',
            subject_identifier='123456789-0', gender=MALE)
        enrollment = mommy.make_recipe(
            'edc_example.enrollment',
            subject_identifier=subject_consent.subject_identifier,
            schedule_name='schedule1')
        appointment = Appointment.objects.get(
            subject_identifier=enrollment.subject_identifier,
            visit_code=self.first_visit.code)
        subject_visit = mommy.make_recipe(
            'edc_example.subjectvisit', appointment=appointment)
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

    def test_delete(self):
        """Asserts delete returns to default entry status."""
        subject_consent = mommy.make_recipe(
            'edc_example.subjectconsent',
            subject_identifier='123456789-0', gender=MALE)
        enrollment = mommy.make_recipe(
            'edc_example.enrollment',
            subject_identifier=subject_consent.subject_identifier,
            schedule_name='schedule1')
        appointment = Appointment.objects.get(
            subject_identifier=enrollment.subject_identifier,
            visit_code=self.first_visit.code)
        subject_visit = mommy.make_recipe(
            'edc_example.subjectvisit', appointment=appointment)
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
        crf_one.delete()
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfTwo._meta.label_lower).entry_status, NOT_REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model=CrfThree._meta.label_lower).entry_status, NOT_REQUIRED)
