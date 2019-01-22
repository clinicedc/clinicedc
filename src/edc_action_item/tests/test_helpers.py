from django.test import TestCase, tag

from ..helpers import ActionItemHelper
from ..model_wrappers import ActionItemModelWrapper
from ..models import ActionItem
from .action_items import register_actions, FormOneAction, CrfOneAction
from .models import FormOne, SubjectIdentifierModel, CrfOne, CrfTwo, FormTwo
from .models import SubjectVisit, Appointment


class TestHelpers(TestCase):
    def setUp(self):
        register_actions()
        self.subject_identifier_model = ActionItem.subject_identifier_model
        ActionItem.subject_identifier_model = "edc_action_item.subjectidentifiermodel"
        self.subject_identifier = "12345"
        SubjectIdentifierModel.objects.create(
            subject_identifier=self.subject_identifier
        )
        self.form_one = FormOne.objects.create(
            subject_identifier=self.subject_identifier
        )
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
        helper = ActionItemHelper(
            action_item=model_wrapper.object, href=model_wrapper.href
        )
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
        helper = ActionItemHelper(
            action_item=model_wrapper.object, href=model_wrapper.href
        )
        context = helper.get_context()
        self.assertEqual(
            context["reference_url"].split("?")[0],
            f"/admin/edc_action_item/formone/add/",
        )
        self.assertEqual(
            context["reference_url"].split("?")[1],
            f"next=edc_action_item:subject_dashboard_url,"
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
            f"next=edc_action_item:subject_dashboard_url,"
            f"subject_identifier&subject_identifier={self.subject_identifier}&"
            f"action_identifier={self.action_item.action_identifier}",
        )

    def test_create_parent_reference_model_instance_then_delete(self):

        form_two = FormTwo.objects.create(
            form_one=self.form_one, subject_identifier=self.subject_identifier
        )
        action_item = ActionItem.objects.get(
            action_identifier=form_two.action_identifier
        )

        model_wrapper = ActionItemModelWrapper(model_obj=action_item)
        helper = ActionItemHelper(
            action_item=model_wrapper.object, href=model_wrapper.href
        )
        context = helper.get_context()
        self.assertEqual(context["reference_obj"], form_two)
        form_two.delete()
        action_item = ActionItem.objects.get(
            action_identifier=form_two.action_identifier
        )
        model_wrapper = ActionItemModelWrapper(model_obj=action_item)
        helper = ActionItemHelper(
            action_item=model_wrapper.object, href=model_wrapper.href
        )
        context = helper.get_context()
        self.assertIsNone(context["reference_obj"])

    def test_create_parent_reference_model_instance(self):
        form_two = FormTwo.objects.create(
            form_one=self.form_one, subject_identifier=self.subject_identifier
        )
        action_item = ActionItem.objects.get(
            action_identifier=form_two.action_identifier
        )
        model_wrapper = ActionItemModelWrapper(model_obj=action_item)
        helper = ActionItemHelper(
            action_item=model_wrapper.object, href=model_wrapper.href
        )
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
        helper = ActionItemHelper(
            action_item=model_wrapper.object, href=model_wrapper.href
        )
        context = helper.get_context()
        self.assertEqual(context["reference_obj"], second_form_two)
        self.assertEqual(context["parent_reference_obj"], first_form_two)
        self.assertEqual(context["related_reference_obj"], self.form_one)
        self.assertTrue(context["reference_url"])
        self.assertTrue(context["parent_reference_url"])
        self.assertTrue(context["related_reference_url"])

    def test_reference_as_crf(self):
        appointment = Appointment.objects.create()
        subject_visit = SubjectVisit.objects.create(
            subject_identifier=self.subject_identifier, appointment=appointment
        )
        crf_one = CrfOne.objects.create(
            subject_identifier=self.subject_identifier, subject_visit=subject_visit
        )
        action_item = ActionItem.objects.get(
            action_identifier=crf_one.action_identifier
        )
        model_wrapper = ActionItemModelWrapper(model_obj=action_item)
        helper = ActionItemHelper(
            action_item=model_wrapper.object, href=model_wrapper.href
        )
        context = helper.get_context()
        self.assertEqual(context["reference_obj"], crf_one)
        self.assertIsNone(context["parent_reference_obj"])
        self.assertIsNone(context["related_reference_obj"])
        self.assertTrue(context["reference_url"])
        self.assertIsNone(context["parent_reference_url"])
        self.assertIsNone(context["related_reference_url"])

    def test_reference_as_crf_create_next_model_instance(self):
        appointment = Appointment.objects.create()
        subject_visit = SubjectVisit.objects.create(
            subject_identifier=self.subject_identifier, appointment=appointment
        )
        crf_one = CrfOne.objects.create(
            subject_identifier=self.subject_identifier, subject_visit=subject_visit
        )
        crf_two = CrfTwo.objects.create(
            subject_identifier=self.subject_identifier, subject_visit=subject_visit
        )
        action_item = ActionItem.objects.get(
            action_identifier=crf_two.action_identifier
        )
        model_wrapper = ActionItemModelWrapper(model_obj=action_item)
        helper = ActionItemHelper(
            action_item=model_wrapper.object, href=model_wrapper.href
        )
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
            f"next=edc_action_item:subject_dashboard_url,"
            f"subject_identifier&subject_identifier={self.subject_identifier}&"
            f"action_identifier={action_item.action_identifier}&"
            f"subject_visit={str(subject_visit.pk)}&"
            f"appointment={str(appointment.pk)}",
        )
