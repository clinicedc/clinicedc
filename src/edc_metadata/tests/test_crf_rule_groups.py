from collections import OrderedDict
from faker import Faker
from django.apps import apps as django_apps
from django.test import TestCase, tag

from edc_constants.constants import MALE
from edc_registration.models import RegisteredSubject
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from ..constants import NOT_REQUIRED, REQUIRED, KEYED
from ..models import CrfMetadata
from ..rules import CrfRuleGroup, CrfRule, P, site_metadata_rules
from .metadata_rules import register_to_site_reference_configs
from .models import Appointment, SubjectVisit
from .models import CrfOne, CrfTwo, Enrollment
from .visit_schedule import visit_schedule

fake = Faker()
edc_registration_app_config = django_apps.get_app_config('edc_registration')


class MyCrfRuleGroup(CrfRuleGroup):

    crfs_car = CrfRule(
        predicate=P('f1', 'eq', 'car'),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=['crftwo'])

    crfs_bicycle = CrfRule(
        predicate=P('f3', 'eq', 'bicycle'),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=['crfthree'])

    class Meta:
        app_label = 'edc_metadata'
        source_model = 'edc_metadata.crfone'


class TestMetadataRules(TestCase):

    def setUp(self):

        register_to_site_reference_configs()
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)

        # note crfs in visit schedule are all set to REQUIRED by default.
        self.schedule = site_visit_schedules.get_schedule(
            visit_schedule_name='visit_schedule',
            schedule_name='schedule')

        site_metadata_rules.registry = OrderedDict()
        site_metadata_rules.register(rule_group_cls=MyCrfRuleGroup)

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

    def test_example1(self):
        """Asserts CrfTwo is REQUIRED if f1==\'car\' as specified.
        """
        subject_visit = self.enroll(gender=MALE)
        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crftwo').entry_status, REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crfthree').entry_status, REQUIRED)

        CrfOne.objects.create(subject_visit=subject_visit, f1='car')

        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crftwo').entry_status, REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crfthree').entry_status, NOT_REQUIRED)

    def test_example2(self):
        """Asserts CrfThree is REQUIRED if f1==\'bicycle\' as specified.
        """

        subject_visit = self.enroll(gender=MALE)
        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crftwo').entry_status, REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crfthree').entry_status, REQUIRED)

        CrfOne.objects.create(subject_visit=subject_visit, f3='bicycle')

        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crftwo').entry_status, NOT_REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crfthree').entry_status, REQUIRED)

        subject_visit.save()

        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crftwo').entry_status, NOT_REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crfthree').entry_status, REQUIRED)

    def test_example4(self):
        """Asserts CrfThree is REQUIRED if f1==\'bicycle\' but then not
        when f1 is changed to \'car\' as specified
        by edc_example.rule_groups.ExampleRuleGroup2."""

        subject_visit = self.enroll(gender=MALE)
        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crftwo').entry_status, REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crfthree').entry_status, REQUIRED)

        crf_one = CrfOne.objects.create(
            subject_visit=subject_visit, f1='not car')

        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crftwo').entry_status, NOT_REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crfthree').entry_status, NOT_REQUIRED)

        crf_one.f1 = 'car'
        crf_one.save()

        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crftwo').entry_status, REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crfthree').entry_status, NOT_REQUIRED)

        crf_one.f3 = 'bicycle'
        crf_one.save()

        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crftwo').entry_status, REQUIRED)
        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crfthree').entry_status, REQUIRED)

    def test_example7(self):
        """Asserts if instance exists, rule is ignored.
        """
        subject_visit = self.enroll(gender=MALE)
        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crftwo').entry_status, REQUIRED)

        CrfTwo.objects.create(
            subject_visit=subject_visit)

        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crftwo').entry_status, KEYED)

        crf_one = CrfOne.objects.create(
            subject_visit=subject_visit, f1='not car')

        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crftwo').entry_status, KEYED)

        crf_one.f1 = 'car'
        crf_one.save()

        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crftwo').entry_status, KEYED)

    def test_delete(self):
        """Asserts delete returns to default entry status.
        """
        subject_visit = self.enroll(gender=MALE)
        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crftwo').entry_status, REQUIRED)

        crf_two = CrfTwo.objects.create(
            subject_visit=subject_visit)

        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crftwo').entry_status, KEYED)

        crf_two.delete()

        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crftwo').entry_status, REQUIRED)

    def test_delete_2(self):
        """Asserts delete returns to entry status of rule for crf_two.
        """
        subject_visit = self.enroll(gender=MALE)
        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crftwo').entry_status, REQUIRED)

        crf_two = CrfTwo.objects.create(
            subject_visit=subject_visit)

        CrfOne.objects.create(
            subject_visit=subject_visit, f1='not car')

        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crftwo').entry_status, KEYED)

        crf_two.delete()

        self.assertEqual(CrfMetadata.objects.get(
            model='edc_metadata.crftwo').entry_status, NOT_REQUIRED)
