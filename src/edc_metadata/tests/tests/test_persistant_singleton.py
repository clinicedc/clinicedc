from collections import OrderedDict
from copy import deepcopy

from dateutil.relativedelta import relativedelta
from django import forms
from django.test import TestCase, override_settings, tag
from edc_reference import site_reference_configs
from edc_utils import get_utcnow
from edc_visit_schedule import site_visit_schedules
from edc_visit_schedule.constants import DAY1, MONTH1, MONTH3, MONTH6, WEEK2

from edc_metadata import (
    KEYED,
    NOT_REQUIRED,
    REQUIRED,
    TargetModelNotScheduledForVisit,
    site_metadata_rules,
)
from edc_metadata.metadata import CrfMetadataGetter

from ...metadata_rules import (
    CrfRule,
    CrfRuleGroup,
    PersistantSingletonMixin,
    PredicateCollection,
)
from ...models import CrfMetadata
from ..models import CrfOne
from ..testcase_mixin import EdcMetadataTestCaseMixin
from ..visit_schedule2 import visit_schedule


class CrfOneForm(forms.ModelForm):
    class Meta:
        model = CrfOne
        fields = "__all__"


@override_settings(
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=get_utcnow() - relativedelta(years=3),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=get_utcnow() + relativedelta(years=3),
)
class TestPersistantSingleton(EdcMetadataTestCaseMixin, TestCase):

    visit_schedule = visit_schedule
    consent_date_months_ago = 24

    def setUp(self):
        # site_visit_schedules._registry = {}
        # site_visit_schedules.loaded = False
        # site_visit_schedules.register(visit_schedule)
        # site_reference_configs.register_from_visit_schedule(
        #     visit_models={"edc_appointment.appointment": "edc_metadata.subjectvisit"}
        # )
        super().setUp()

        self.data = dict(
            subject_visit=self.subject_visit,
            report_datetime=self.subject_visit.report_datetime,
            f1="blah",
            f2="blah",
            f3="blah",
        )

    def get_rule_group(self):
        class Predicates(PersistantSingletonMixin, PredicateCollection):
            app_label = "edc_metadata"
            visit_model = "edc_metadata.subjectvisit"

            def crfone_required(self, visit, **kwargs):
                model = f"{self.app_label}.crfone"
                return self.persistant_singleton_required(
                    visit, model=model, evaluate_after=[DAY1]
                )

        pc = Predicates()

        class RuleGroup(CrfRuleGroup):
            crfone = CrfRule(
                predicate=pc.crfone_required,
                consequence=REQUIRED,
                alternative=NOT_REQUIRED,
                target_models=["crfone"],
            )

            class Meta:
                app_label = "edc_metadata"
                source_model = "edc_metadata.subjectvisit"

        return RuleGroup

    @tag("1")
    def test_baseline_not_required(self):
        site_metadata_rules.registry = OrderedDict()
        site_metadata_rules.register(self.get_rule_group())
        form = CrfOneForm(data=self.data)
        form.is_valid()
        self.assertEqual({}, form._errors)
        self.assertRaises(TargetModelNotScheduledForVisit, form.save)

        crf_metadata_getter = CrfMetadataGetter(appointment=self.subject_visit.appointment)
        self.assertFalse(
            crf_metadata_getter.metadata_objects.filter(
                model="edc_metadata.crfone", entry_status=REQUIRED
            ).exists()
        )

    @tag("1")
    def test_1005_required(self):
        site_metadata_rules.registry = OrderedDict()
        site_metadata_rules.register(self.get_rule_group())
        subject_visit = self.get_next_subject_visit(self.subject_visit)
        self.assertEqual(subject_visit.visit_code, WEEK2)
        crf_metadata_getter = CrfMetadataGetter(appointment=subject_visit.appointment)
        self.assertTrue(
            crf_metadata_getter.metadata_objects.filter(model="edc_metadata.crfone").exists()
        )
        self.assertEqual(
            crf_metadata_getter.metadata_objects.get(
                model="edc_metadata.crfone", visit_code=WEEK2
            ).entry_status,
            REQUIRED,
        )

        self.assertEqual(CrfMetadata.objects.filter(model="edc_metadata.crfone").count(), 1)

        data = deepcopy(self.data)
        data.update(subject_visit=subject_visit, report_datetime=subject_visit.report_datetime)
        form = CrfOneForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)
        form.save()
        self.assertTrue(
            crf_metadata_getter.metadata_objects.filter(
                model="edc_metadata.crfone", entry_status=KEYED
            ).exists()
        )

    @tag("1")
    def test_visit_required_if_not_submitted(self):
        site_metadata_rules.registry = OrderedDict()
        site_metadata_rules.register(self.get_rule_group())
        subject_visit = self.get_next_subject_visit(self.subject_visit)
        self.assertEqual(subject_visit.visit_code, WEEK2)
        self.assertEqual(CrfMetadata.objects.filter(model="edc_metadata.crfone").count(), 1)
        self.assertEqual(
            [(WEEK2, REQUIRED)],
            [
                (obj.visit_code, obj.entry_status)
                for obj in CrfMetadata.objects.filter(model="edc_metadata.crfone").order_by(
                    "timepoint"
                )
            ],
        )

        subject_visit = self.get_next_subject_visit(subject_visit)
        self.assertEqual(subject_visit.visit_code, MONTH1)
        self.assertEqual(CrfMetadata.objects.filter(model="edc_metadata.crfone").count(), 2)
        self.assertEqual(
            [(WEEK2, NOT_REQUIRED), (MONTH1, REQUIRED)],
            [
                (obj.visit_code, obj.entry_status)
                for obj in CrfMetadata.objects.filter(model="edc_metadata.crfone").order_by(
                    "timepoint"
                )
            ],
        )

        subject_visit = self.get_next_subject_visit(subject_visit)
        self.assertEqual(subject_visit.visit_code, MONTH3)
        self.assertEqual(CrfMetadata.objects.filter(model="edc_metadata.crfone").count(), 3)
        self.assertEqual(
            [(WEEK2, NOT_REQUIRED), (MONTH1, NOT_REQUIRED), (MONTH3, REQUIRED)],
            [
                (obj.visit_code, obj.entry_status)
                for obj in CrfMetadata.objects.filter(model="edc_metadata.crfone").order_by(
                    "timepoint"
                )
            ],
        )

        subject_visit = self.get_next_subject_visit(subject_visit)
        self.assertEqual(subject_visit.visit_code, MONTH6)
        self.assertEqual(CrfMetadata.objects.filter(model="edc_metadata.crfone").count(), 4)
        self.assertEqual(
            [
                (WEEK2, NOT_REQUIRED),
                (MONTH1, NOT_REQUIRED),
                (MONTH3, NOT_REQUIRED),
                (MONTH6, REQUIRED),
            ],
            [
                (obj.visit_code, obj.entry_status)
                for obj in CrfMetadata.objects.filter(model="edc_metadata.crfone").order_by(
                    "timepoint"
                )
            ],
        )

    @tag("1")
    def test_1010_required_if_not_submitted(self):
        site_metadata_rules.registry = OrderedDict()
        site_metadata_rules.register(self.get_rule_group())
        subject_visit = self.get_next_subject_visit(self.subject_visit)
        subject_visit = self.get_next_subject_visit(subject_visit)
        self.assertEqual(subject_visit.visit_code, MONTH1)
        crf_metadata_getter = CrfMetadataGetter(appointment=subject_visit.appointment)
        self.assertTrue(
            crf_metadata_getter.metadata_objects.filter(model="edc_metadata.crfone").exists()
        )
        self.assertEqual(
            crf_metadata_getter.metadata_objects.get(
                model="edc_metadata.crfone", visit_code=MONTH1
            ).entry_status,
            REQUIRED,
        )
        data = deepcopy(self.data)
        data.update(subject_visit=subject_visit, report_datetime=subject_visit.report_datetime)
        form = CrfOneForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)
        form.save()
        self.assertTrue(
            crf_metadata_getter.metadata_objects.filter(
                model="edc_metadata.crfone", entry_status=KEYED
            ).exists()
        )

    def test_1030_required_if_not_submitted(self):
        subject_visit = self.get_next_subject_visit(self.subject_visit)
        subject_visit = self.get_next_subject_visit(subject_visit)
        subject_visit = self.get_next_subject_visit(subject_visit)
        self.assertEqual(subject_visit.visit_code, MONTH3)
        crf_metadata_getter = CrfMetadataGetter(appointment=subject_visit.appointment)
        self.assertTrue(
            crf_metadata_getter.metadata_objects.filter(model="edc_metadata.crfone").exists()
        )
        self.assertEqual(
            crf_metadata_getter.metadata_objects.get(
                model="edc_metadata.crfone", visit_code=MONTH3
            ).entry_status,
            REQUIRED,
        )
        data = deepcopy(self.data)
        data.update(subject_visit=subject_visit, report_datetime=subject_visit.report_datetime)
        form = CrfOneForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)
        form.save()
        self.assertTrue(
            crf_metadata_getter.metadata_objects.filter(
                model="edc_metadata.crfone", entry_status=KEYED
            ).exists()
        )

    def test_1030_not_required_if_submitted(self):
        subject_visit_1005 = self.get_next_subject_visit(self.subject_visit)
        subject_visit_1010 = self.get_next_subject_visit(subject_visit_1005)
        subject_visit_1030 = self.get_next_subject_visit(subject_visit_1010)
        self.assertEqual(subject_visit_1030.visit_code, MONTH3)
        crf_metadata_getter = CrfMetadataGetter(appointment=subject_visit_1030.appointment)
        self.assertTrue(
            crf_metadata_getter.metadata_objects.filter(
                model="edc_metadata.crfone", entry_status=REQUIRED
            ).exists()
        )
        data = deepcopy(self.data)
        data.update(
            subject_visit=subject_visit_1010,
            report_datetime=subject_visit_1010.report_datetime,
        )
        form = CrfOneForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)
        form.save()
        crf_metadata_getter = CrfMetadataGetter(appointment=subject_visit_1005.appointment)
        self.assertTrue(
            crf_metadata_getter.metadata_objects.filter(
                model="edc_metadata.crfone", entry_status=NOT_REQUIRED
            ).exists()
        )
        crf_metadata_getter = CrfMetadataGetter(appointment=subject_visit_1010.appointment)
        self.assertTrue(
            crf_metadata_getter.metadata_objects.filter(
                model="edc_metadata.crfone", entry_status=KEYED
            ).exists()
        )
        crf_metadata_getter = CrfMetadataGetter(appointment=subject_visit_1030.appointment)
        self.assertTrue(
            crf_metadata_getter.metadata_objects.filter(
                model="edc_metadata.crfone", entry_status=NOT_REQUIRED
            ).exists()
        )
