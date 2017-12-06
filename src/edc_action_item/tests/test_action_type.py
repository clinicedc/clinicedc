from django.test import TestCase, tag
from django.conf import settings
from edc_constants.constants import CLOSED
from edc_model_wrapper import ModelWrapper

from ..action_handler import ActionHandler
from ..action_items import FormOneAction, FormTwoAction, FormThreeAction
from ..models import ActionItem, ActionType
from ..site_action_items import site_action_items
from ..templatetags.action_item_extras import action_item_with_popover
from .models import FormOne, FormTwo, FormThree, SubjectIdentifierModel


class TestActionType(TestCase):

    def setUp(self):
        site_action_items.populated_action_type = False
        self.subject_identifier_model = ActionItem.subject_identifier_model
        ActionItem.subject_identifier_model = 'edc_action_item.subjectidentifiermodel'
        self.subject_identifier = '12345'
        SubjectIdentifierModel.objects.create(
            subject_identifier=self.subject_identifier)
        self.assertEqual(0, ActionType.objects.all().count())
        self.assertIn(FormOneAction.name, site_action_items.registry)
        self.assertIn(FormTwoAction.name, site_action_items.registry)
        self.assertIn(FormThreeAction.name, site_action_items.registry)

    @tag('4')
    def test_populate_action_types(self):
        site_action_items.populate_action_type()
        self.assertEqual(ActionType.objects.all().count(), 5)

    @tag('4')
    def test_populate_action_types_in_handler(self):
        model_obj = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        ActionHandler(model_obj=model_obj)
        self.assertEqual(ActionType.objects.all().count(), 5)

    @tag('4')
    def test_creates_own_action(self):
        action_type = FormOneAction.action_type()
        obj = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        self.assertTrue(
            ActionItem.objects.filter(action_identifier=obj.action_identifier))
        self.assertEqual(ActionItem.objects.filter(
            subject_identifier=self.subject_identifier,
            action_type=action_type).count(), 1)

    @tag('4')
    def test_does_not_duplicate_own_action(self):
        action_type = FormOneAction.action_type()
        self.assertEqual(ActionItem.objects.all().count(), 0)
        ActionItem.objects.create(
            subject_identifier=self.subject_identifier,
            action_type=action_type)
        self.assertEqual(ActionItem.objects.all().count(), 1)
        obj = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        self.assertTrue(
            ActionItem.objects.filter(
                action_identifier=obj.action_identifier))
        self.assertEqual(ActionItem.objects.filter(
            subject_identifier=self.subject_identifier,
            action_type=action_type).count(), 1)

    @tag('4')
    def test_finds_existing_actions(self):
        """Finds existing actions even in many are created in advance.
        """
        action_type = FormOneAction.action_type()
        FormTwoAction.action_type()
        FormThreeAction.action_type()
        self.assertEqual(ActionItem.objects.all().count(), 0)
        for _ in range(0, 5):
            ActionItem.objects.create(
                subject_identifier=self.subject_identifier,
                action_type=action_type)
        self.assertEqual(ActionItem.objects.filter(
            action_type=action_type).count(), 5)

        self.assertEqual(ActionItem.objects.filter(
            action_type=action_type,
            reference_identifier__isnull=True).count(), 5)

        for i in range(0, 5):
            with self.subTest(index=i):
                obj = FormOne.objects.create(
                    subject_identifier=self.subject_identifier)
                self.assertTrue(
                    ActionItem.objects.filter(action_identifier=obj.action_identifier))
                self.assertEqual(ActionItem.objects.filter(
                    action_type=action_type,
                    reference_identifier__isnull=True).count(), 5 - (i + 1))
                self.assertEqual(ActionItem.objects.filter(
                    action_type=action_type).count(), 5)

        obj = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        self.assertTrue(
            ActionItem.objects.filter(action_identifier=obj.action_identifier))
        self.assertEqual(ActionItem.objects.filter(
            action_type=action_type,
            reference_identifier__isnull=True).count(), 0)
        self.assertEqual(ActionItem.objects.filter(
            action_type=action_type).count(), 6)

    @tag('4')
    def test_creates_next_actions(self):
        f1_action_type = FormOneAction.action_type()
        f2_action_type = FormTwoAction.action_type()
        f3_action_type = FormThreeAction.action_type()
        FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        self.assertEqual(ActionItem.objects.all().count(), 3)
        self.assertEqual(ActionItem.objects.filter(
            subject_identifier=self.subject_identifier,
            action_type=f1_action_type).count(), 1)
        self.assertEqual(ActionItem.objects.filter(
            subject_identifier=self.subject_identifier,
            action_type=f2_action_type).count(), 1)
        self.assertEqual(ActionItem.objects.filter(
            subject_identifier=self.subject_identifier,
            action_type=f3_action_type).count(), 1)

    def test_creates_next_actions2(self):
        form_one = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        FormTwo.objects.create(
            subject_identifier=self.subject_identifier,
            form_one=form_one)
        FormThree.objects.create(
            subject_identifier=self.subject_identifier)

    def test_action_is_closed_if_model_creates_action(self):
        f1_action_type = FormOneAction.action_type()
        f2_action_type = FormTwoAction.action_type()
        f3_action_type = FormThreeAction.action_type()
        form_one = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        FormTwo.objects.create(
            subject_identifier=self.subject_identifier,
            form_one=form_one)
        FormThree.objects.create(
            subject_identifier=self.subject_identifier)
        obj = ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            action_type=f1_action_type)
        self.assertEqual(obj.status, CLOSED)
        obj = ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            action_type=f2_action_type,
            status=CLOSED)
        self.assertEqual(obj.status, CLOSED)
        obj = ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            action_type=f3_action_type)
        self.assertEqual(obj.status, CLOSED)

    def test_reference_model_url(self):
        obj = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        action_item = ActionItem.objects.get(
            action_identifier=obj.action_identifier)
        url = FormOneAction(model_obj=obj).reference_model_url(
            action_item=action_item)
        self.assertEqual(
            url,
            f'/admin/edc_action_item/formone/add/?')

    def test_reference_model_url2(self):
        form_one = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        obj = FormTwo.objects.create(
            subject_identifier=self.subject_identifier,
            form_one=form_one)
        action_item = ActionItem.objects.get(
            action_identifier=obj.action_identifier)
        url = FormTwoAction(model_obj=obj).reference_model_url(
            action_item=action_item)
        self.assertEqual(
            url,
            f'/admin/edc_action_item/formtwo/add/?')

    def test_reference_model_url3(self):
        form_one = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        obj = FormTwo.objects.create(
            subject_identifier=self.subject_identifier,
            form_one=form_one)
        action_item = ActionItem.objects.get(
            action_identifier=obj.action_identifier)
        url = FormTwoAction(model_obj=obj).reference_model_url(
            action_item=action_item,
            subject_identifier=self.subject_identifier)
        self.assertEqual(
            url,
            f'/admin/edc_action_item/formtwo/add/?subject_identifier={self.subject_identifier}')

    def test_popover_templatetag(self):

        class ActionItemModelWrapper(ModelWrapper):

            model = 'edc_action_item.actionitem'
            next_url_attrs = ['subject_identifier']
            next_url_name = settings.DASHBOARD_URL_NAMES.get(
                'subject_dashboard_url')

            @property
            def subject_identifier(self):
                return self.object.subject_identifier

        action_type = FormOneAction.action_type()
        obj = ActionItem.objects.create(
            subject_identifier=self.subject_identifier,
            action_type=action_type)
        wrapper = ActionItemModelWrapper(model_obj=obj)
        action_item_with_popover(wrapper)
