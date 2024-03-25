from django.apps import apps as django_apps
from django.test import TestCase
from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_visit_tracking.constants import SCHEDULED

from edc_action_item.models import ActionItem
from edc_action_item.utils import (
    get_parent_reference_obj,
    get_reference_obj,
    get_related_reference_obj,
)

from ..action_items import CrfOneAction, register_actions
from ..models import CrfOne, CrfTwo, FormOne, FormTwo
from ..test_case_mixin import TestCaseMixin


class TestHelpers(TestCaseMixin, TestCase):
    def setUp(self):
        site_consents.registry = {}
        register_actions()
        self.subject_identifier = self.fake_enroll()
        self.form_one = FormOne.objects.create(subject_identifier=self.subject_identifier)
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
        action_item = ActionItem.objects.get(action_identifier=form_two.action_identifier)
        self.assertEqual(get_reference_obj(action_item), form_two)
        form_two.delete()
        action_item = ActionItem.objects.get(action_identifier=form_two.action_identifier)
        self.assertIsNone(get_reference_obj(action_item))

    def test_create_parent_reference_model_instance(self):
        form_two = FormTwo.objects.create(
            form_one=self.form_one, subject_identifier=self.subject_identifier
        )
        action_item = ActionItem.objects.get(action_identifier=form_two.action_identifier)
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
        self.enroll()
        appointment = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[0]
        subject_visit = django_apps.get_model(
            "edc_visit_tracking.subjectvisit"
        ).objects.create(appointment=appointment, reason=SCHEDULED)
        crf_one = CrfOne.objects.create(subject_visit=subject_visit)
        action_item = ActionItem.objects.get(action_identifier=crf_one.action_identifier)
        self.assertEqual(get_reference_obj(action_item), crf_one)
        self.assertIsNone(get_parent_reference_obj(action_item))
        self.assertIsNone(get_related_reference_obj(action_item))

    def test_reference_as_crf_create_next_model_instance(self):
        self.enroll()
        appointment = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[0]
        subject_visit = django_apps.get_model(
            "edc_visit_tracking.subjectvisit"
        ).objects.create(appointment=appointment, reason=SCHEDULED)
        crf_one = CrfOne.objects.create(subject_visit=subject_visit)
        crf_two = CrfTwo.objects.create(subject_visit=subject_visit)
        action_item = ActionItem.objects.get(action_identifier=crf_two.action_identifier)
        self.assertEqual(get_reference_obj(action_item), crf_two)
        self.assertEqual(get_parent_reference_obj(action_item), crf_one)
        self.assertIsNone(get_related_reference_obj(action_item))
