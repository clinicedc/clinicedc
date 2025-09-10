from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from faker import Faker

from edc_consent import site_consents
from edc_constants.constants import MALE
from edc_facility.import_holidays import import_holidays
from edc_metadata import KEYED, NOT_REQUIRED, REQUIRED
from edc_metadata.metadata_handler import MetadataHandlerError
from edc_metadata.metadata_rules import site_metadata_rules
from edc_metadata.models import CrfMetadata
from edc_metadata.tests.crf_rule_groups import (
    CrfRuleGroupOne,
    CrfRuleGroupThree,
    CrfRuleGroupTwo,
)
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import CrfOne, CrfTwo, PrnOne
from clinicedc_tests.visit_schedules.visit_schedule_metadata.visit_schedule import (
    get_visit_schedule,
)

fake = Faker()
utc_tz = ZoneInfo("UTC")


@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=utc_tz))
class CrfRuleGroupTestCase(TestCase):
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
        site_metadata_rules.register(rule_group_cls=CrfRuleGroupOne)
        site_metadata_rules.register(rule_group_cls=CrfRuleGroupTwo)
        site_metadata_rules.register(rule_group_cls=CrfRuleGroupThree)

    def get_next_subject_visit(self, subject_visit):
        return SubjectVisit.objects.create(
            appointment=self.appointment.next,
            reason=SCHEDULED,
            subject_identifier=subject_visit.subject_identifier,
            visit_schedule_name=self.appointment.next.visit_schedule_name,
            schedule_name=self.appointment.next.schedule_name,
            visit_code=self.appointment.next.visit_code,
            visit_code_sequence=self.appointment.next.visit_code_sequence,
        )

    def test_default_d1(self):
        """Test before any CRFs are submitted"""
        self.helper.enroll_to_baseline(gender=MALE)
        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crfone").entry_status,
            REQUIRED,
        )
        # set to NOT_REQUIRED by CrfRuleGroupOne.crfs_car
        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crftwo").entry_status,
            NOT_REQUIRED,
        )
        # set to NOT_REQUIRED by CrfRuleGroupOne.crfs_bicycle
        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crfthree").entry_status,
            NOT_REQUIRED,
        )
        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crffour").entry_status,
            REQUIRED,
        )
        # set to NOT_REQUIRED by CrfRuleGroupTwo.crfs_truck
        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crffive").entry_status,
            NOT_REQUIRED,
        )

    def test_example1(self):
        """Asserts CrfTwo is REQUIRED if f1==\'car\' as specified."""
        subject_visit = self.helper.enroll_to_baseline(gender=MALE)
        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crftwo").entry_status,
            NOT_REQUIRED,
        )
        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crfthree").entry_status,
            NOT_REQUIRED,
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
            NOT_REQUIRED,
        )
        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crfthree").entry_status,
            NOT_REQUIRED,
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
            NOT_REQUIRED,
        )
        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crfthree").entry_status,
            NOT_REQUIRED,
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
            NOT_REQUIRED,
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
        self.assertEqual(metadata_obj.entry_status, NOT_REQUIRED)

        # note, does not automatically recreate
        metadata_obj.delete()
        self.assertRaises(
            ObjectDoesNotExist, CrfMetadata.objects.get, model="edc_metadata.crftwo"
        )

        CrfTwo.objects.create(subject_visit=subject_visit)

        metadata_obj = CrfMetadata.objects.get(model="edc_metadata.crftwo")
        self.assertEqual(metadata_obj.entry_status, KEYED)

    def test_delete(self):
        """Asserts delete returns to default entry status."""
        subject_visit = self.enroll(gender=MALE)
        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crftwo").entry_status,
            NOT_REQUIRED,
        )

        crf_two = CrfTwo.objects.create(subject_visit=subject_visit)

        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crftwo").entry_status,
            KEYED,
        )

        crf_two.delete()

        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crftwo").entry_status,
            NOT_REQUIRED,
        )

    def test_delete_2(self):
        """Asserts delete returns to entry status of rule for crf_two."""
        subject_visit = self.enroll(gender=MALE)
        self.assertEqual(
            CrfMetadata.objects.get(model="edc_metadata.crftwo").entry_status,
            NOT_REQUIRED,
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

    def test_prn_is_created_as_not_required_by_default(self):
        """Asserts handles PRNs correctly"""
        # create both visits before going back to add crf_one
        subject_visit = self.enroll(gender=MALE)
        self.assertEqual(
            CrfMetadata.objects.get(
                model="edc_metadata.prnone",
                visit_code=subject_visit.visit_code,
                visit_code_sequence=subject_visit.visit_code_sequence,
            ).entry_status,
            NOT_REQUIRED,
        )

    def test_prn_rule_acts_on_correct_visit(self):
        """Asserts handles PRNs correctly"""
        # create both visits before going back to add crf_one
        subject_visit = self.enroll(gender=MALE)

        # rule = prnone is required if crf_one.f1 == holden

        # not required by default @ 1000
        self.assertEqual(
            CrfMetadata.objects.get(
                model="edc_metadata.prnone",
                visit_code=subject_visit.visit_code,
                visit_code_sequence=subject_visit.visit_code_sequence,
            ).entry_status,
            NOT_REQUIRED,
        )
        # not required by default @ 2000
        subject_visit_two = self.get_next_subject_visit(subject_visit)
        self.assertEqual(
            CrfMetadata.objects.get(
                model="edc_metadata.prnone",
                visit_code=subject_visit_two.visit_code,
                visit_code_sequence=subject_visit_two.visit_code_sequence,
            ).entry_status,
            NOT_REQUIRED,
        )

        # submit crf_one to trigger rule
        crf_one = CrfOne.objects.create(subject_visit=subject_visit, f1="holden")

        # should be required @ 1000
        self.assertEqual(
            CrfMetadata.objects.get(
                model="edc_metadata.prnone",
                visit_code=subject_visit.visit_code,
                visit_code_sequence=subject_visit.visit_code_sequence,
            ).entry_status,
            REQUIRED,
        )
        # should still be `not required` @ 2000
        self.assertEqual(
            CrfMetadata.objects.get(
                model="edc_metadata.prnone",
                visit_code=subject_visit_two.visit_code,
                visit_code_sequence=subject_visit_two.visit_code_sequence,
            ).entry_status,
            NOT_REQUIRED,
        )

        crf_one.f1 = "caufield"  # @1000
        crf_one.save()

        # should change back to not required @ 1000
        self.assertEqual(
            CrfMetadata.objects.get(
                model="edc_metadata.prnone",
                visit_code=subject_visit.visit_code,
                visit_code_sequence=subject_visit.visit_code_sequence,
            ).entry_status,
            NOT_REQUIRED,
        )

        # should still be `not required` @ 2000
        self.assertEqual(
            CrfMetadata.objects.get(
                model="edc_metadata.prnone",
                visit_code=subject_visit_two.visit_code,
                visit_code_sequence=subject_visit_two.visit_code_sequence,
            ).entry_status,
            NOT_REQUIRED,
        )

        crf_one.f1 = "holden"
        crf_one.save()
        # should be required @ 1000
        self.assertEqual(
            CrfMetadata.objects.get(
                model="edc_metadata.prnone",
                visit_code=subject_visit.visit_code,
                visit_code_sequence=subject_visit.visit_code_sequence,
            ).entry_status,
            REQUIRED,
        )
        # should still be `not required` @ 2000
        self.assertEqual(
            CrfMetadata.objects.get(
                model="edc_metadata.prnone",
                visit_code=subject_visit_two.visit_code,
                visit_code_sequence=subject_visit_two.visit_code_sequence,
            ).entry_status,
            NOT_REQUIRED,
        )

    def test_prn_rule_acts_on_correct_visit_2000(self):
        """Asserts handles PRNs correctly"""
        # create 1000 then add crf_one then create 2000
        subject_visit = self.enroll(gender=MALE)

        self.assertEqual(
            1, CrfMetadata.objects.filter(model="edc_metadata.prnone").count()
        )

        crf_one = CrfOne.objects.create(subject_visit=subject_visit, f1="caufield")
        self.assertEqual(
            1,
            CrfMetadata.objects.filter(
                model="edc_metadata.prnone", entry_status=NOT_REQUIRED
            ).count(),
        )

        subject_visit_two = self.get_next_subject_visit(subject_visit)

        self.assertEqual(
            2, CrfMetadata.objects.filter(model="edc_metadata.prnone").count()
        )
        self.assertEqual(
            2,
            CrfMetadata.objects.filter(
                model="edc_metadata.prnone", entry_status=NOT_REQUIRED
            ).count(),
        )

        crf_one.f1 = "holden"
        crf_one.save()
        # should be required @ 1000
        self.assertEqual(
            CrfMetadata.objects.get(
                model="edc_metadata.prnone",
                visit_code=subject_visit.visit_code,
                visit_code_sequence=subject_visit.visit_code_sequence,
            ).entry_status,
            REQUIRED,
        )
        # should still be `not required` @ 2000
        self.assertEqual(
            CrfMetadata.objects.get(
                model="edc_metadata.prnone",
                visit_code=subject_visit_two.visit_code,
                visit_code_sequence=subject_visit_two.visit_code_sequence,
            ).entry_status,
            NOT_REQUIRED,
        )

    def test_crf_cannot_be_saved_if_not_in_visits_crfs(self):
        subject_visit = self.enroll(gender=MALE)
        self.assertEqual(
            1, CrfMetadata.objects.filter(model="edc_metadata.prnone").count()
        )
        subject_visit_two = self.get_next_subject_visit(subject_visit)
        self.assertEqual(
            2, CrfMetadata.objects.filter(model="edc_metadata.prnone").count()
        )

        # note: crf_one is not listed as a crf for visit 2000
        # trigger exception just to prove that the crf_one cannot be saved
        # if not listed in crfs for visit 2000
        try:
            CrfOne.objects.create(subject_visit=subject_visit_two, f1="caufield")
        except MetadataHandlerError:
            pass

    def test_prn_can_be_submitted_if_now_required(self):
        subject_visit = self.enroll(gender=MALE)
        self.assertEqual(
            1, CrfMetadata.objects.filter(model="edc_metadata.prnone").count()
        )
        self.get_next_subject_visit(subject_visit)
        self.assertEqual(
            2, CrfMetadata.objects.filter(model="edc_metadata.prnone").count()
        )
        CrfOne.objects.create(subject_visit=subject_visit, f1="holden")
        PrnOne.objects.create(subject_visit=subject_visit)

    def test_prn_resets_on_delete(self):
        subject_visit = self.enroll(gender=MALE)
        crf_one = CrfOne.objects.create(subject_visit=subject_visit, f1="holden")
        crf_one.delete()
        self.assertEqual(
            CrfMetadata.objects.get(
                model="edc_metadata.prnone",
                visit_code=subject_visit.visit_code,
                visit_code_sequence=subject_visit.visit_code_sequence,
            ).entry_status,
            NOT_REQUIRED,
        )
