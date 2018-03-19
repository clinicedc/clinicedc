from django.test import TestCase, tag
from edc_constants.constants import CLOSED, NEW

from ..action import ActionItemGetter, ActionItemObjectDoesNotExist
from ..models import ActionItem, ActionType
from ..site_action_items import site_action_items
from .action_items import FormZeroAction, FormThreeAction, register_actions
from .models import SubjectIdentifierModel, FormOne, FormTwo


class TestActionItemGetter(TestCase):

    def setUp(self):
        register_actions()
        self.subject_identifier_model = ActionItem.subject_identifier_model
        ActionItem.subject_identifier_model = 'edc_action_item.subjectidentifiermodel'
        self.subject_identifier = '12345'
        SubjectIdentifierModel.objects.create(
            subject_identifier=self.subject_identifier)
        # force create action types
        for action_cls in site_action_items.registry.values():
            action_cls.action_type()

    def test_init(self):
        self.assertRaises(
            ActionItemObjectDoesNotExist,
            ActionItemGetter, FormZeroAction,
            subject_identifier=self.subject_identifier)

    def test_getter_finds_action_item_with_action_identifier(self):
        action_type = ActionType.objects.get(name='submit-form-zero')
        obj = ActionItem.objects.create(
            subject_identifier=self.subject_identifier,
            action_type=action_type)
        getter = ActionItemGetter(
            FormZeroAction,
            action_identifier=obj.action_identifier)
        self.assertEqual(
            getter.model_obj.action_identifier,
            obj.action_identifier)

    def test_getter_finds_available_action_item(self):
        action_type = ActionType.objects.get(name='submit-form-zero')
        obj = ActionItem.objects.create(
            subject_identifier=self.subject_identifier,
            action_type=action_type)
        getter = ActionItemGetter(
            FormZeroAction,
            subject_identifier=obj.subject_identifier)
        self.assertEqual(
            getter.model_obj.action_identifier,
            obj.action_identifier)

    def test_getter_finds_parent_action_and_next(self):
        """
        Note: form_one creates new form two, form three actions.
        form-two creates a new form-two action."""

        self.assertEqual(ActionItem.objects.all().count(), 0)
        # parent
        form_one_obj = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        self.assertIsNotNone(form_one_obj.action_identifier)
        # parent is updated
        ActionItem.objects.filter(
            status=CLOSED, action_type__name='submit-form-one')

        # parent created next actions
        self.assertEqual(ActionItem.objects.filter(
            action_type__name='submit-form-two',
            status=NEW).count(), 1)
        self.assertEqual(ActionItem.objects.filter(
            action_type__name='submit-form-three',
            status=NEW).count(), 1)

        # FormTwo finds 'submit-form-two' action item
        FormTwo.objects.create(
            subject_identifier=self.subject_identifier,
            form_one=form_one_obj)
        self.assertEqual(ActionItem.objects.filter(
            action_type__name='submit-form-two',
            status=CLOSED).count(), 1)
        self.assertEqual(ActionItem.objects.filter(
            action_type__name='submit-form-two',
            status=NEW).count(), 1)
        self.assertEqual(ActionItem.objects.filter(
            action_type__name='submit-form-three',
            status=NEW).count(), 1)

    def test_getter_finds_available_action_item2(self):
        self.assertEqual(ActionItem.objects.all().count(), 0)
        form_one_obj = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        self.assertIsNotNone(form_one_obj.action_identifier)
        self.assertEqual(ActionItem.objects.all().count(), 3)

    def test_getter_finds_available_action_item3(self):

        self.assertEqual(ActionItem.objects.all().count(), 0)
        form_one_obj = FormOne.objects.create(
            subject_identifier=self.subject_identifier)

        FormOne.objects.create(subject_identifier=self.subject_identifier)

        getter = ActionItemGetter(
            FormThreeAction,
            subject_identifier=self.subject_identifier,
            parent_reference_identifier=form_one_obj.tracking_identifier)

        self.assertEqual(
            getter.model_obj.parent_reference_identifier, form_one_obj.tracking_identifier)

    def test_getter_parent_action_and_next(self):
        """
        Note: form_one creates new form two, form three actions.
        form-two creates a new form-two action."""

        # parent
        form_one_obj = FormOne.objects.create(
            subject_identifier=self.subject_identifier)

        action_items = [(obj.action_type.name, obj.status,
                         obj.reference_identifier,
                         obj.parent_reference_identifier)
                        for obj in ActionItem.objects.all()]
        self.assertEqual(len(action_items), 3)
        self.assertIn(
            ('submit-form-one', CLOSED, form_one_obj.tracking_identifier, None),
            action_items)
        self.assertIn(
            ('submit-form-three', NEW, None, form_one_obj.tracking_identifier),
            action_items)
        self.assertIn(
            ('submit-form-two', NEW, None, form_one_obj.tracking_identifier),
            action_items)

        # next
        form_two_obj = FormTwo.objects.create(
            subject_identifier=self.subject_identifier,
            form_one=form_one_obj)
        action_items = [(obj.action_type.name, obj.status,
                         obj.reference_identifier,
                         obj.parent_reference_identifier)
                        for obj in ActionItem.objects.all()]
        self.assertEqual(len(action_items), 4)
        self.assertIn(
            ('submit-form-two', CLOSED, form_two_obj.tracking_identifier,
             form_one_obj.tracking_identifier),
            action_items)
