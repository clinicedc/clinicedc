from collections import OrderedDict

from django.apps import apps as django_apps
from django.test import TestCase
from edc_constants.constants import MALE
from edc_facility.import_holidays import import_holidays
from edc_reference.site_reference import site_reference_configs
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from faker import Faker

from edc_metadata import KEYED, NOT_REQUIRED, REQUIRED
from edc_metadata.models import CrfMetadata

from ...metadata_rules import CrfRule, CrfRuleGroup, P, site_metadata_rules
from ..models import Appointment, CrfOne, CrfTwo, SubjectConsent, SubjectVisit
from ..reference_configs import register_to_site_reference_configs
from ..visit_schedule import visit_schedule

fake = Faker()
edc_registration_app_config = django_apps.get_app_config("edc_registration")


class CrfRuleGroupOne(CrfRuleGroup):

    crfs_car = CrfRule(
        predicate=P("f1", "eq", "car"),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=["crftwo"],
    )

    crfs_bicycle = CrfRule(
        predicate=P("f3", "eq", "bicycle"),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=["crfthree"],
    )

    class Meta:
        app_label = "edc_metadata"
        source_model = "edc_metadata.crfone"


class CrfRuleGroupTwo(CrfRuleGroup):

    crfs_truck = CrfRule(
        predicate=P("f1", "eq", "truck"),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=["crffive"],
    )

    crfs_train = CrfRule(
        predicate=P("f1", "eq", "train"),
        consequence=REQUIRED,
        alternative=NOT_REQUIRED,
        target_models=["crfsix"],
    )

    class Meta:
        app_label = "edc_metadata"
        source_model = "edc_metadata.crfone"


class CrfRuleGroupTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        import_holidays()
        register_to_site_reference_configs()
        return super().setUpClass()

    def setUp(self):
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "edc_metadata.subjectvisit"}
        )

        # note crfs in visit schedule are all set to REQUIRED by default.
        _, self.schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_metadata.onschedule"
        )

        site_metadata_rules.registry = OrderedDict()
        site_metadata_rules.register(rule_group_cls=CrfRuleGroupOne)
        site_metadata_rules.register(rule_group_cls=CrfRuleGroupTwo)

    def enroll(self, gender=None):
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

    def test_example1(self):
        """Asserts CrfTwo is REQUIRED if f1==\'car\' as specified."""
        subject_visit = self.enroll(gender=MALE)
        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crftwo").entry_status,
            REQUIRED,
        )
        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crfthree").entry_status,
            REQUIRED,
        )

        CrfOne.objects.create(subject_visit=subject_visit, f1="car")

        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crftwo").entry_status,
            REQUIRED,
        )
        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crfthree").entry_status,
            NOT_REQUIRED,
        )

    def test_example2(self):
        """Asserts CrfThree is REQUIRED if f1==\'bicycle\' as specified."""

        subject_visit = self.enroll(gender=MALE)
        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crftwo").entry_status,
            REQUIRED,
        )
        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crfthree").entry_status,
            REQUIRED,
        )

        CrfOne.objects.create(subject_visit=subject_visit, f3="bicycle")

        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crftwo").entry_status,
            NOT_REQUIRED,
        )
        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crfthree").entry_status,
            REQUIRED,
        )

        subject_visit.save()

        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crftwo").entry_status,
            NOT_REQUIRED,
        )
        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crfthree").entry_status,
            REQUIRED,
        )

    def test_example4(self):
        """Asserts CrfThree is REQUIRED if f1==\'bicycle\' but then not
        when f1 is changed to \'car\' as specified
        by edc_example.rule_groups.ExampleRuleGroup2."""

        subject_visit = self.enroll(gender=MALE)
        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crftwo").entry_status,
            REQUIRED,
        )
        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crfthree").entry_status,
            REQUIRED,
        )

        crf_one = CrfOne.objects.create(subject_visit=subject_visit, f1="not car")

        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crftwo").entry_status,
            NOT_REQUIRED,
        )
        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crfthree").entry_status,
            NOT_REQUIRED,
        )

        crf_one.f1 = "car"
        crf_one.save()

        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crftwo").entry_status,
            REQUIRED,
        )
        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crfthree").entry_status,
            NOT_REQUIRED,
        )

        crf_one.f3 = "bicycle"
        crf_one.save()

        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crftwo").entry_status,
            REQUIRED,
        )
        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crfthree").entry_status,
            REQUIRED,
        )

    def test_keyed_instance_ignores_rules(self):
        """Asserts if instance exists, rule is ignored."""
        subject_visit = self.enroll(gender=MALE)
        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crftwo").entry_status,
            REQUIRED,
        )

        CrfTwo.objects.create(subject_visit=subject_visit)

        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crftwo").entry_status,
            KEYED,
        )

        crf_one = CrfOne.objects.create(subject_visit=subject_visit, f1="not car")

        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crftwo").entry_status,
            KEYED,
        )

        crf_one.f1 = "car"
        crf_one.save()

        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crftwo").entry_status,
            KEYED,
        )

    def test_recovers_from_missing_metadata(self):
        subject_visit = self.enroll(gender=MALE)
        metadata_obj = CrfMetadata.objects.get(model="edc_metadata.crftwo")
        self.assertEqual(metadata_obj.entry_status, REQUIRED)

        metadata_obj.delete()

        CrfTwo.objects.create(subject_visit=subject_visit)

        metadata_obj = CrfMetadata.objects.get(model="edc_metadata.crftwo")
        self.assertEqual(metadata_obj.entry_status, KEYED)

    def test_delete(self):
        """Asserts delete returns to default entry status."""
        subject_visit = self.enroll(gender=MALE)
        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crftwo").entry_status,
            REQUIRED,
        )

        crf_two = CrfTwo.objects.create(subject_visit=subject_visit)

        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crftwo").entry_status,
            KEYED,
        )

        crf_two.delete()

        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crftwo").entry_status,
            REQUIRED,
        )

    def test_delete_2(self):
        """Asserts delete returns to entry status of rule for crf_two."""
        subject_visit = self.enroll(gender=MALE)
        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crftwo").entry_status,
            REQUIRED,
        )

        crf_two = CrfTwo.objects.create(subject_visit=subject_visit)

        CrfOne.objects.create(subject_visit=subject_visit, f1="not car")

        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crftwo").entry_status,
            KEYED,
        )

        crf_two.delete()

        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crftwo").entry_status,
            NOT_REQUIRED,
        )
