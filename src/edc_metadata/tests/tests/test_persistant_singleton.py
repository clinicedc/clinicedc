from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import CrfFour, CrfSix
from clinicedc_tests.visit_schedules.visit_schedule_metadata.visit_schedule2 import (
    get_visit_schedule,
)
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.test import TestCase, override_settings, tag

from edc_appointment.constants import IN_PROGRESS_APPT, INCOMPLETE_APPT
from edc_consent import site_consents
from edc_constants.constants import INCOMPLETE
from edc_facility.import_holidays import import_holidays
from edc_metadata import KEYED, NOT_REQUIRED, REQUIRED
from edc_metadata.metadata import CrfMetadataGetter
from edc_metadata.metadata_handler import MetadataHandlerError
from edc_metadata.metadata_rules import (
    CrfRule,
    CrfRuleGroup,
    PersistantSingletonMixin,
    site_metadata_rules,
)
from edc_metadata.models import CrfMetadata
from edc_visit_schedule.constants import DAY1, MONTH1, MONTH3, MONTH6, WEEK2
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit


class CrfSixForm(forms.ModelForm):
    class Meta:
        model = CrfSix
        fields = "__all__"


class CrfFourForm(forms.ModelForm):
    class Meta:
        model = CrfFour
        fields = "__all__"


class TestCaseMixin:
    @staticmethod
    def get_next_subject_visit(subject_visit):
        appointment = subject_visit.appointment
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save()
        appointment.refresh_from_db()
        next_appointment = appointment.next_by_timepoint
        next_appointment.appt_status = IN_PROGRESS_APPT
        next_appointment.save()
        subject_visit = SubjectVisit(
            appointment=next_appointment,
            reason=SCHEDULED,
            report_datetime=next_appointment.appt_datetime,
            visit_code=next_appointment.visit_code,
            visit_code_sequence=next_appointment.visit_code_sequence,
        )
        subject_visit.save()
        subject_visit.refresh_from_db()
        return subject_visit


utc_tz = ZoneInfo("UTC")


@tag("metadata")
@override_settings(SITE_ID=10)
@time_machine.travel(datetime(2019, 8, 11, 8, 00, tzinfo=utc_tz))
class TestPersistantSingleton(TestCaseMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        visit_schedule = get_visit_schedule(consent_v1)
        site_visit_schedules.register(visit_schedule)

        site_metadata_rules.registry = {}
        site_metadata_rules.register(self.rule_group)

        self.user = User.objects.create(username="erik")

        helper = Helper()
        self.subject_visit = helper.enroll_to_baseline(
            visit_schedule_name=visit_schedule.name,
            schedule_name="schedule",
        )
        self.subject_identifier = self.subject_visit.subject_identifier
        self.data = dict(
            subject_visit=self.subject_visit,
            report_datetime=self.subject_visit.report_datetime,
            f1="blah",
            f2="blah",
            f3="blah",
            site=Site.objects.get(id=settings.SITE_ID),
            crf_status=INCOMPLETE,
        )

    @property
    def rule_group(self):
        class Predicates(PersistantSingletonMixin):
            def crfone_required(self, visit, **kwargs):  # noqa
                model = "clinicedc_tests.crffour"
                return self.persistant_singleton_required(
                    visit, model=model, exclude_visit_codes=[DAY1]
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
                app_label = "clinicedc_tests"
                source_model = "edc_visit_tracking.subjectvisit"

        return RuleGroup

    def test_baseline_not_required(self):
        site_metadata_rules.registry = {}
        site_metadata_rules.register(self.rule_group)
        form = CrfSixForm(data=self.data)
        form.is_valid()
        self.assertEqual({}, form._errors)
        self.assertRaises(MetadataHandlerError, form.save)

        crf_metadata_getter = CrfMetadataGetter(appointment=self.subject_visit.appointment)
        self.assertFalse(
            crf_metadata_getter.metadata_objects.filter(
                model="clinicedc_tests.crfsix", entry_status=REQUIRED
            ).exists()
        )

    @tag("metadata3")
    def test_1005_required(self):
        site_metadata_rules.registry = {}
        site_metadata_rules.register(self.rule_group)
        subject_visit = self.get_next_subject_visit(self.subject_visit)
        traveller = time_machine.travel(subject_visit.report_datetime)
        traveller.start()
        self.assertEqual(subject_visit.visit_code, WEEK2)
        crf_metadata_getter = CrfMetadataGetter(appointment=subject_visit.appointment)
        self.assertTrue(
            crf_metadata_getter.metadata_objects.filter(
                model="clinicedc_tests.crffour"
            ).exists()
        )
        self.assertEqual(
            crf_metadata_getter.metadata_objects.get(
                model="clinicedc_tests.crffour", visit_code=WEEK2
            ).entry_status,
            REQUIRED,
        )

        self.assertEqual(
            CrfMetadata.objects.filter(model="clinicedc_tests.crffour").count(), 1
        )

        data = deepcopy(self.data)
        data.update(subject_visit=subject_visit, report_datetime=subject_visit.report_datetime)
        form = CrfFourForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)
        form.save()
        self.assertTrue(
            crf_metadata_getter.metadata_objects.filter(
                model="clinicedc_tests.crffour", entry_status=KEYED
            ).exists()
        )
        traveller.stop()

    def test_visit_required_if_not_submitted(self):
        site_metadata_rules.registry = {}
        site_metadata_rules.register(self.rule_group)
        subject_visit = self.get_next_subject_visit(self.subject_visit)
        traveller = time_machine.travel(subject_visit.report_datetime)
        traveller.start()
        self.assertEqual(subject_visit.visit_code, WEEK2)
        self.assertEqual(
            CrfMetadata.objects.filter(model="clinicedc_tests.crffour").count(), 1
        )
        self.assertEqual(
            [(WEEK2, REQUIRED)],
            [
                (obj.visit_code, obj.entry_status)
                for obj in CrfMetadata.objects.filter(
                    model="clinicedc_tests.crffour"
                ).order_by("timepoint")
            ],
        )
        subject_visit = self.get_next_subject_visit(subject_visit)
        traveller.stop()
        traveller = time_machine.travel(subject_visit.report_datetime)
        traveller.start()
        self.assertEqual(subject_visit.visit_code, MONTH1)
        self.assertEqual(
            CrfMetadata.objects.filter(model="clinicedc_tests.crffour").count(), 2
        )
        self.assertEqual(
            [(WEEK2, NOT_REQUIRED), (MONTH1, REQUIRED)],
            [
                (obj.visit_code, obj.entry_status)
                for obj in CrfMetadata.objects.filter(
                    model="clinicedc_tests.crffour"
                ).order_by("timepoint")
            ],
        )

        subject_visit = self.get_next_subject_visit(subject_visit)
        traveller.stop()
        traveller = time_machine.travel(subject_visit.report_datetime)
        traveller.start()
        self.assertEqual(subject_visit.visit_code, MONTH3)
        self.assertEqual(
            CrfMetadata.objects.filter(model="clinicedc_tests.crffour").count(), 3
        )
        self.assertEqual(
            [(WEEK2, NOT_REQUIRED), (MONTH1, NOT_REQUIRED), (MONTH3, REQUIRED)],
            [
                (obj.visit_code, obj.entry_status)
                for obj in CrfMetadata.objects.filter(
                    model="clinicedc_tests.crffour"
                ).order_by("timepoint")
            ],
        )

        subject_visit = self.get_next_subject_visit(subject_visit)
        traveller.stop()
        traveller = time_machine.travel(subject_visit.report_datetime)
        traveller.start()
        self.assertEqual(subject_visit.visit_code, MONTH6)
        self.assertEqual(
            CrfMetadata.objects.filter(model="clinicedc_tests.crffour").count(), 4
        )
        self.assertEqual(
            [
                (WEEK2, NOT_REQUIRED),
                (MONTH1, NOT_REQUIRED),
                (MONTH3, NOT_REQUIRED),
                (MONTH6, REQUIRED),
            ],
            [
                (obj.visit_code, obj.entry_status)
                for obj in CrfMetadata.objects.filter(
                    model="clinicedc_tests.crffour"
                ).order_by("timepoint")
            ],
        )

    def test_1010_required_if_not_submitted(self):
        site_metadata_rules.registry = {}
        site_metadata_rules.register(self.rule_group)
        subject_visit = self.get_next_subject_visit(self.subject_visit)
        subject_visit = self.get_next_subject_visit(subject_visit)
        traveller = time_machine.travel(subject_visit.report_datetime)
        traveller.start()
        self.assertEqual(subject_visit.visit_code, MONTH1)
        crf_metadata_getter = CrfMetadataGetter(appointment=subject_visit.appointment)
        self.assertTrue(
            crf_metadata_getter.metadata_objects.filter(
                model="clinicedc_tests.crffour"
            ).exists()
        )
        self.assertEqual(
            crf_metadata_getter.metadata_objects.get(
                model="clinicedc_tests.crffour", visit_code=MONTH1
            ).entry_status,
            REQUIRED,
        )
        data = deepcopy(self.data)
        data.update(subject_visit=subject_visit, report_datetime=subject_visit.report_datetime)
        form = CrfFourForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)
        form.save()
        self.assertTrue(
            crf_metadata_getter.metadata_objects.filter(
                model="clinicedc_tests.crffour", entry_status=KEYED
            ).exists()
        )
        traveller.stop()

    def test_1030_required_if_not_submitted(self):
        site_metadata_rules.registry = {}
        site_metadata_rules.register(self.rule_group)
        subject_visit = self.get_next_subject_visit(self.subject_visit)
        subject_visit = self.get_next_subject_visit(subject_visit)
        subject_visit = self.get_next_subject_visit(subject_visit)
        traveller = time_machine.travel(subject_visit.report_datetime)
        traveller.start()
        self.assertEqual(subject_visit.visit_code, MONTH3)
        crf_metadata_getter = CrfMetadataGetter(appointment=subject_visit.appointment)
        self.assertTrue(
            crf_metadata_getter.metadata_objects.filter(
                model="clinicedc_tests.crffour"
            ).exists()
        )
        self.assertEqual(
            crf_metadata_getter.metadata_objects.get(
                model="clinicedc_tests.crffour", visit_code=MONTH3
            ).entry_status,
            REQUIRED,
        )
        data = deepcopy(self.data)
        data.update(subject_visit=subject_visit, report_datetime=subject_visit.report_datetime)
        form = CrfFourForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)
        form.save()
        self.assertTrue(
            crf_metadata_getter.metadata_objects.filter(
                model="clinicedc_tests.crffour", entry_status=KEYED
            ).exists()
        )
        traveller.stop()

    def test_1030_not_required_if_submitted(self):
        site_metadata_rules.registry = {}
        site_metadata_rules.register(self.rule_group)
        subject_visit_1005 = self.get_next_subject_visit(self.subject_visit)
        subject_visit_1010 = self.get_next_subject_visit(subject_visit_1005)
        subject_visit_1030 = self.get_next_subject_visit(subject_visit_1010)
        self.assertEqual(subject_visit_1030.visit_code, MONTH3)
        crf_metadata_getter = CrfMetadataGetter(appointment=subject_visit_1030.appointment)
        self.assertTrue(
            crf_metadata_getter.metadata_objects.filter(
                model="clinicedc_tests.crffour", entry_status=REQUIRED
            ).exists()
        )
        data = deepcopy(self.data)
        data.update(
            subject_visit=subject_visit_1010,
            report_datetime=subject_visit_1010.report_datetime,
        )
        traveller = time_machine.travel(subject_visit_1010.report_datetime)
        traveller.start()
        form = CrfFourForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)
        form.save()
        crf_metadata_getter = CrfMetadataGetter(appointment=subject_visit_1005.appointment)
        self.assertTrue(
            crf_metadata_getter.metadata_objects.filter(
                model="clinicedc_tests.crffour", entry_status=NOT_REQUIRED
            ).exists()
        )
        crf_metadata_getter = CrfMetadataGetter(appointment=subject_visit_1010.appointment)
        self.assertTrue(
            crf_metadata_getter.metadata_objects.filter(
                model="clinicedc_tests.crffour", entry_status=KEYED
            ).exists()
        )
        crf_metadata_getter = CrfMetadataGetter(appointment=subject_visit_1030.appointment)
        self.assertTrue(
            crf_metadata_getter.metadata_objects.filter(
                model="clinicedc_tests.crffour", entry_status=NOT_REQUIRED
            ).exists()
        )
