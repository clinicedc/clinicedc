from django.apps import apps as django_apps
from django.test import TestCase
from edc_appointment.models import Appointment
from edc_visit_tracking.constants import SCHEDULED

from edc_action_item.helpers import ActionItemHelper
from edc_action_item.model_wrappers import ActionItemModelWrapper
from edc_action_item.models import ActionItem

from ..action_items import CrfOneAction, FormOneAction, register_actions
from ..models import CrfOne, CrfTwo, FormOne, FormTwo
from ..test_case_mixin import TestCaseMixin


class TestHelpers(TestCaseMixin, TestCase):
    def setUp(self):
        register_actions()
        self.subject_identifier = self.fake_enroll()
        self.form_one = FormOne.objects.create(subject_identifier=self.subject_identifier)
        self.action_item = ActionItem.objects.get(
            action_identifier=self.form_one.action_identifier
        )
        self.model_wrapper = ActionItemModelWrapper(model_obj=self.action_item)

    def test_init(self):
        helper = ActionItemHelper(
            action_item=self.model_wrapper.object, href=self.model_wrapper.href
        )
        self.assertTrue(helper.get_context())

    def test_new_action(self):
        action = CrfOneAction(subject_identifier=self.subject_identifier)

        self.assertIsNone(action.reference_obj)

        model_wrapper = ActionItemModelWrapper(model_obj=action.action_item)
        helper = ActionItemHelper(action_item=model_wrapper.object, href=model_wrapper.href)
        context = helper.get_context()
        self.assertIsNone(context["reference_obj"])
        self.assertIsNone(context["parent_reference_obj"])
        self.assertIsNone(context["related_reference_obj"])
        self.assertTrue(context["reference_url"])
        self.assertIsNone(context["parent_reference_url"])
        self.assertIsNone(context["related_reference_url"])

    def test_new_action_url(self):
        action = FormOneAction(subject_identifier=self.subject_identifier)
        action_item = action.action_item
        model_wrapper = ActionItemModelWrapper(model_obj=action_item)
        helper = ActionItemHelper(action_item=model_wrapper.object, href=model_wrapper.href)
        context = helper.get_context()
        self.assertEqual(
            context["reference_url"].split("?")[0],
            "/admin/edc_action_item/formone/add/",
        )
        self.assertEqual(
            context["reference_url"].split("?")[1],
            "next=edc_action_item:subject_dashboard_url,"
            f"subject_identifier&subject_identifier={self.subject_identifier}&"
            f"action_identifier={action_item.action_identifier}",
        )

    def test_action_with_reference_model_instance(self):
        helper = ActionItemHelper(
            action_item=self.model_wrapper.object, href=self.model_wrapper.href
        )
        context = helper.get_context()
        self.assertTrue(context["reference_obj"])
        self.assertIsNone(context["parent_reference_obj"])
        self.assertIsNone(context["related_reference_obj"])
        self.assertTrue(context["reference_url"])
        self.assertIsNone(context["parent_reference_url"])
        self.assertIsNone(context["related_reference_url"])

    def test_reference_obj_and_url(self):
        helper = ActionItemHelper(
            action_item=self.model_wrapper.object, href=self.model_wrapper.href
        )
        context = helper.get_context()
        self.assertEqual(context["reference_obj"], self.form_one)
        self.assertEqual(
            context["reference_url"].split("?")[0],
            f"/admin/edc_action_item/formone/{str(self.form_one.id)}/change/",
        )

        self.assertEqual(
            context["reference_url"].split("?")[1],
            "next=edc_action_item:subject_dashboard_url,"
            f"subject_identifier&subject_identifier={self.subject_identifier}&"
            f"action_identifier={self.action_item.action_identifier}",
        )

    def test_create_parent_reference_model_instance_then_delete(self):
        form_two = FormTwo.objects.create(
            form_one=self.form_one, subject_identifier=self.subject_identifier
        )
        action_item = ActionItem.objects.get(action_identifier=form_two.action_identifier)

        model_wrapper = ActionItemModelWrapper(model_obj=action_item)
        helper = ActionItemHelper(action_item=model_wrapper.object, href=model_wrapper.href)
        context = helper.get_context()
        self.assertEqual(context["reference_obj"], form_two)
        form_two.delete()
        action_item = ActionItem.objects.get(action_identifier=form_two.action_identifier)
        model_wrapper = ActionItemModelWrapper(model_obj=action_item)
        helper = ActionItemHelper(action_item=model_wrapper.object, href=model_wrapper.href)
        context = helper.get_context()
        self.assertIsNone(context["reference_obj"])

    def test_create_parent_reference_model_instance(self):
        form_two = FormTwo.objects.create(
            form_one=self.form_one, subject_identifier=self.subject_identifier
        )
        action_item = ActionItem.objects.get(action_identifier=form_two.action_identifier)
        model_wrapper = ActionItemModelWrapper(model_obj=action_item)
        helper = ActionItemHelper(action_item=model_wrapper.object, href=model_wrapper.href)
        context = helper.get_context()
        self.assertEqual(context["reference_obj"], form_two)
        self.assertEqual(context["parent_reference_obj"], self.form_one)
        self.assertEqual(context["related_reference_obj"], self.form_one)
        self.assertTrue(context["reference_url"])
        self.assertTrue(context["parent_reference_url"])
        self.assertTrue(context["related_reference_url"])

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
        model_wrapper = ActionItemModelWrapper(model_obj=action_item)
        helper = ActionItemHelper(action_item=model_wrapper.object, href=model_wrapper.href)
        context = helper.get_context()
        self.assertEqual(context["reference_obj"], second_form_two)
        self.assertEqual(context["parent_reference_obj"], first_form_two)
        self.assertEqual(context["related_reference_obj"], self.form_one)
        self.assertTrue(context["reference_url"])
        self.assertTrue(context["parent_reference_url"])
        self.assertTrue(context["related_reference_url"])

    def test_reference_as_crf(self):
        self.enroll()
        appointment = Appointment.objects.all().order_by("timepoint")[0]
        subject_visit = django_apps.get_model(
            "edc_visit_tracking.subjectvisit"
        ).objects.create(appointment=appointment, reason=SCHEDULED)
        crf_one = CrfOne.objects.create(subject_visit=subject_visit)
        action_item = ActionItem.objects.get(action_identifier=crf_one.action_identifier)
        model_wrapper = ActionItemModelWrapper(model_obj=action_item)
        helper = ActionItemHelper(action_item=model_wrapper.object, href=model_wrapper.href)
        context = helper.get_context()
        self.assertEqual(context["reference_obj"], crf_one)
        self.assertIsNone(context["parent_reference_obj"])
        self.assertIsNone(context["related_reference_obj"])
        self.assertTrue(context["reference_url"])
        self.assertIsNone(context["parent_reference_url"])
        self.assertIsNone(context["related_reference_url"])

    def test_reference_as_crf_create_next_model_instance(self):
        subject_identifier = self.enroll()
        appointment = Appointment.objects.all().order_by("timepoint")[0]
        subject_visit = django_apps.get_model(
            "edc_visit_tracking.subjectvisit"
        ).objects.create(appointment=appointment, reason=SCHEDULED)
        crf_one = CrfOne.objects.create(subject_visit=subject_visit)
        crf_two = CrfTwo.objects.create(subject_visit=subject_visit)
        action_item = ActionItem.objects.get(action_identifier=crf_two.action_identifier)
        model_wrapper = ActionItemModelWrapper(model_obj=action_item)
        helper = ActionItemHelper(action_item=model_wrapper.object, href=model_wrapper.href)
        context = helper.get_context()
        self.assertEqual(context["reference_obj"], crf_two)
        self.assertEqual(context["parent_reference_obj"], crf_one)
        self.assertIsNone(context["related_reference_obj"])
        self.assertTrue(context["reference_url"])
        self.assertTrue(context["parent_reference_url"])
        self.assertIsNone(context["related_reference_url"])

        self.assertEqual(
            context["parent_reference_url"].split("?")[0],
            f"/admin/edc_action_item/crfone/{str(crf_one.id)}/change/",
        )
        self.assertEqual(
            context["parent_reference_url"].split("?")[1],
            "next=edc_action_item:subject_dashboard_url,"
            f"subject_identifier&subject_identifier={subject_identifier}&"
            f"action_identifier={action_item.action_identifier}&"
            f"subject_visit={str(subject_visit.pk)}&"
            f"appointment={str(appointment.pk)}",
        )
