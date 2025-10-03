from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import CrfThree
from clinicedc_tests.visit_schedules.visit_schedule_metadata.visit_schedule import (
    get_visit_schedule,
)
from django.test import TestCase, override_settings, tag
from faker import Faker

from edc_consent import site_consents
from edc_constants.constants import FEMALE, MALE
from edc_facility.import_holidays import import_holidays
from edc_metadata.metadata_rules import PF, P
from edc_registration.models import RegisteredSubject
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

fake = Faker()


utc_tz = ZoneInfo("UTC")


@tag("metadata")
@override_settings(SITE_ID=10)
@time_machine.travel(datetime(2019, 8, 11, 8, 00, tzinfo=utc_tz))
class TestPredicates(TestCase):
    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super().setUpClass()

    def setUp(self):
        helper = Helper()
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(get_visit_schedule(consent_v1))
        # note crfs in visit schedule are all set to REQUIRED by default.
        self.visit_schedule, self.schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_visit_schedule.onschedule"
        )
        self.subject_visit_female = helper.enroll_to_baseline(
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            gender=FEMALE,
        )
        self.subject_visit_male = helper.enroll_to_baseline(
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            gender=MALE,
        )
        self.subject_identifier_female = self.subject_visit_female.subject_identifier
        self.subject_identifier_male = self.subject_visit_male.subject_identifier
        self.registered_subject_female = RegisteredSubject.objects.get(
            subject_identifier=self.subject_identifier_female
        )
        self.registered_subject_male = RegisteredSubject.objects.get(
            subject_identifier=self.subject_identifier_male
        )

    def test_p_male(self):
        opts = dict(
            source_model="clinicedc_tests.crfthree",
            registered_subject=self.registered_subject_male,
            visit=self.subject_visit_male,
        )
        self.assertTrue(P("gender", "eq", MALE)(**opts))
        self.assertFalse(P("gender", "eq", FEMALE)(**opts))

    def test_p_female(self):
        opts = dict(
            source_model="clinicedc_tests.crfthree",
            registered_subject=self.registered_subject_female,
            visit=self.subject_visit_female,
        )
        self.assertTrue(P("gender", "eq", FEMALE)(**opts))
        self.assertFalse(P("gender", "eq", MALE)(**opts))

    def test_p_reason(self):
        opts = dict(
            source_model="clinicedc_tests.crfthree",
            registered_subject=self.registered_subject_male,
            visit=self.subject_visit_male,
        )
        self.assertTrue(P("reason", "eq", SCHEDULED)(**opts))

    def test_p_with_field_on_source_keyed_value_none(self):
        opts = dict(
            source_model="clinicedc_tests.crfthree",
            registered_subject=self.registered_subject_female,
            visit=self.subject_visit_female,
        )
        CrfThree.objects.create(subject_visit=self.subject_visit_female)
        self.assertFalse(P("f1", "eq", "car")(**opts))

    def test_p_with_field_on_source_keyed_with_value(self):
        opts = dict(
            source_model="clinicedc_tests.crfthree",
            registered_subject=self.registered_subject_female,
            visit=self.subject_visit_female,
        )
        CrfThree.objects.create(subject_visit=self.subject_visit_female, f1="bicycle")
        self.assertFalse(P("f1", "eq", "car")(**opts))

    def test_p_with_field_on_source_keyed_with_matching_value(self):
        opts = dict(
            source_model="clinicedc_tests.crfthree",
            registered_subject=self.registered_subject_female,
            visit=self.subject_visit_female,
        )
        CrfThree.objects.create(subject_visit=self.subject_visit_female, f1="car")
        self.assertTrue(P("f1", "eq", "car")(**opts))

    def test_p_with_field_on_source_keyed_with_multiple_values_in(self):
        opts = dict(
            source_model="clinicedc_tests.crfthree",
            registered_subject=self.registered_subject_female,
            visit=self.subject_visit_female,
        )
        CrfThree.objects.create(subject_visit=self.subject_visit_female, f1="car")
        self.assertTrue(P("f1", "in", ["car", "bicycle"])(**opts))

    def test_p_with_field_on_source_keyed_with_multiple_values_not_in(self):
        opts = dict(
            source_model="clinicedc_tests.crfthree",
            registered_subject=self.registered_subject_female,
            visit=self.subject_visit_female,
        )
        CrfThree.objects.create(subject_visit=self.subject_visit_female, f1="truck")
        self.assertFalse(P("f1", "in", ["car", "bicycle"])(**opts))

    def test_pf(self):
        opts = dict(
            source_model="clinicedc_tests.crfthree",
            registered_subject=self.registered_subject_female,
            visit=self.subject_visit_female,
        )
        CrfThree.objects.create(subject_visit=self.subject_visit_female, f1="car")
        self.assertTrue(PF("f1", func=lambda x: x == "car")(**opts))
        self.assertFalse(PF("f1", func=lambda x: x == "bicycle")(**opts))

    def test_pf_2(self):
        def func(f1, f2):
            return f1 == "car" and f2 == "bicycle"

        opts = dict(
            source_model="clinicedc_tests.crfthree",
            registered_subject=self.registered_subject_female,
            visit=self.subject_visit_female,
        )
        CrfThree.objects.create(
            subject_visit=self.subject_visit_female, f1="car", f2="bicycle"
        )
        self.assertTrue(PF("f1", "f2", func=func)(**opts))
