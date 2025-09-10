from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from django.test import TestCase, override_settings, tag

from edc_action_item.models import ActionItem
from edc_action_item.tests.test_case_mixin import TestCaseMixin
from edc_action_item.utils import (
    get_parent_reference_obj,
    get_reference_obj,
    get_related_reference_obj,
)
from edc_consent import site_consents
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from clinicedc_tests.action_items import CrfOneAction, register_actions
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import CrfOne, CrfTwo, FormOne, FormTwo
from clinicedc_tests.visit_schedules.visit_schedule_action_item import (
    get_visit_schedule,
)

utc_tz = ZoneInfo("UTC")


@tag("action_item")
@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=utc_tz))
@override_settings(SITE_ID=30)
class TestHelpers(TestCaseMixin, TestCase):
    def setUp(self):
        self.helper = Helper()

        site_consents.registry = {}
        site_consents.register(consent_v1)

        register_actions()

        visit_schedule = get_visit_schedule(consent_v1)
        schedule = visit_schedule.schedules.get("schedule_action_item")
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)

        self.subject_visit = self.helper.enroll_to_baseline(
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
            consent_definition=consent_v1,
        )
        self.subject_identifier = self.subject_visit.subject_identifier
        self.form_one = FormOne.objects.create(
            subject_identifier=self.subject_identifier
        )
        self.action_item = ActionItem.objects.get(
            action_identifier=self.form_one.action_identifier
        )

    def test_new_action(self):
        CrfOneAction(subject_identifier=self.subject_identifier)
        self.assertIsNone(get_reference_obj(None))
        self.assertIsNone(get_parent_reference_obj(None))
        self.assertIsNone(get_related_reference_obj(None))

    def test_create_parent_reference_model_instance_then_delete(self):
        form_two = FormTwo.objects.create(
            form_one=self.form_one, subject_identifier=self.subject_identifier
        )
        action_item = ActionItem.objects.get(
            action_identifier=form_two.action_identifier
        )
        self.assertEqual(get_reference_obj(action_item), form_two)
        form_two.delete()
        action_item = ActionItem.objects.get(
            action_identifier=form_two.action_identifier
        )
        self.assertIsNone(get_reference_obj(action_item))

    def test_create_parent_reference_model_instance(self):
        form_two = FormTwo.objects.create(
            form_one=self.form_one, subject_identifier=self.subject_identifier
        )
        action_item = ActionItem.objects.get(
            action_identifier=form_two.action_identifier
        )
        self.assertEqual(get_reference_obj(action_item), form_two)
        self.assertEqual(get_parent_reference_obj(action_item), self.form_one)
        self.assertEqual(get_related_reference_obj(action_item), self.form_one)

    def test_create_next_parent_reference_model_instance(self):
        first_form_two = FormTwo.objects.create(
            form_one=self.form_one, subject_identifier=self.subject_identifier
        )
        second_form_two = FormTwo.objects.create(
            form_one=self.form_one, subject_identifier=self.subject_identifier
        )
        action_item = ActionItem.objects.get(
            action_identifier=second_form_two.action_identifier
        )
        self.assertEqual(get_reference_obj(action_item), second_form_two)
        self.assertEqual(get_parent_reference_obj(action_item), first_form_two)
        self.assertEqual(get_related_reference_obj(action_item), self.form_one)

    def test_reference_as_crf(self):
        crf_one = CrfOne.objects.create(subject_visit=self.subject_visit)
        action_item = ActionItem.objects.get(
            action_identifier=crf_one.action_identifier
        )
        self.assertEqual(get_reference_obj(action_item), crf_one)
        self.assertIsNone(get_parent_reference_obj(action_item))
        self.assertIsNone(get_related_reference_obj(action_item))

    def test_reference_as_crf_create_next_model_instance(self):
        crf_one = CrfOne.objects.create(subject_visit=self.subject_visit)
        crf_two = CrfTwo.objects.create(subject_visit=self.subject_visit)
        action_item = ActionItem.objects.get(
            action_identifier=crf_two.action_identifier
        )
        self.assertEqual(get_reference_obj(action_item), crf_two)
        self.assertEqual(get_parent_reference_obj(action_item), crf_one)
        self.assertIsNone(get_related_reference_obj(action_item))
