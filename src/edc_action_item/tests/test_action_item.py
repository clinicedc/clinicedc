from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag
from edc_constants.constants import NEW, OPEN

from ..action import Action, ActionError, ActionFieldError
from ..action_handler import ModelMissingActionClass
from ..action_items import ReminderAction
from ..forms import ActionItemForm
from ..models import ActionItem, ActionItemUpdate, SubjectDoesNotExist, ActionType
from ..site_action_items import site_action_items
from .models import SubjectIdentifierModel, TestModelWithTrackingIdentifierButNoActionClass
from .models import TestModel, TestModelWithAction
from .models import TestModelWithoutMixin


class TestActionItem(TestCase):

    def setUp(self):
        site_action_items.populated_action_type = False
        site_action_items.populate_action_type()
        self.subject_identifier_model = ActionItem.subject_identifier_model
        ActionItem.subject_identifier_model = 'edc_action_item.subjectidentifiermodel'
        self.subject_identifier = '12345'
        SubjectIdentifierModel.objects.create(
            subject_identifier=self.subject_identifier)
        self.action_type = ActionType.objects.all().first()

    def tearDown(self):
        ActionItem.subject_identifier_model = self.subject_identifier_model

    def test_create(self):
        self.assertRaises(
            SubjectDoesNotExist,
            ActionItem.objects.create)
        obj = ActionItem.objects.create(
            subject_identifier=self.subject_identifier,
            action_type=self.action_type,
            reference_model='edc_action_item.testmodel')
        self.assertTrue(obj.action_identifier.startswith('AC'))
        self.assertEqual(obj.status, NEW)
        self.assertIsNotNone(obj.report_datetime)

    def test_identifier_not_changed(self):
        obj = ActionItem.objects.create(
            subject_identifier=self.subject_identifier,
            action_type=self.action_type)
        action_identifier = obj.action_identifier
        obj.save()
        try:
            obj = ActionItem.objects.get(action_identifier=action_identifier)
        except ObjectDoesNotExist:
            self.fail('ActionItem unexpectedly does not exist')

    def test_form(self):
        obj = ActionItem.objects.create(
            subject_identifier=self.subject_identifier,
            action_type=self.action_type,
            name='a new action item')
        data = obj.__dict__
        data.update(action_type=obj.action_type.id)
        form = ActionItemForm(data=obj.__dict__, instance=obj)
        self.assertEqual(form.errors, {})

    def test_changes_status_from_new_to_open_on_edit(self):
        obj = ActionItem.objects.create(
            subject_identifier=self.subject_identifier,
            action_type=self.action_type,
            name='a new action item')
        ActionItemUpdate.objects.create(action_item=obj)
        ActionItemUpdate.objects.create(action_item=obj)
        ActionItemUpdate.objects.create(action_item=obj)
        data = obj.__dict__
        data.update(action_type=obj.action_type.id)
        data['status'] = NEW
        form = ActionItemForm(data=obj.__dict__, instance=obj)
        self.assertTrue(form.is_valid())
        self.assertNotIn('status', form.errors)
        self.assertEqual(form.cleaned_data.get('status'), OPEN)

    def test_action(self):

        class MyNonPrnAction(Action):
            name = 'prn_action'
            model = None

        # create action
        action = MyNonPrnAction(subject_identifier=self.subject_identifier)
        self.assertIsNotNone(action.object)

        # create action but incorrect instantiate with a model instance
        class MyPrnActionMissingModel(Action):
            name = 'prn_action'

        self.assertRaises(
            SubjectDoesNotExist,
            MyPrnActionMissingModel, model_obj=TestModel())

        # create instance but instantiate with wrong model type
        class MyPrnActionWrongModel(Action):
            name = 'prn_action'
            prn_form_action = True
            model = 'blah.blah'

        self.assertRaises(
            ActionError,
            MyPrnActionWrongModel, model_obj=TestModel())

        # create instance but declare/instantiate with model class that has not
        # actions
        class MyPrnAction(Action):
            name = 'prn_action'
            prn_form_action = True
            model = 'edc_action_item.TestModelWithTrackingIdentifierButNoActionClass'

        self.assertRaises(
            ModelMissingActionClass,
            TestModelWithTrackingIdentifierButNoActionClass.objects.create,
            subject_identifier=self.subject_identifier)

    def test_model_using_action_cls_without_model(self):

        self.assertEqual(TestModelWithAction.action_cls, ReminderAction)
        self.assertIsNone(ReminderAction.model)

        obj = TestModelWithAction.objects.create(
            subject_identifier=self.subject_identifier)

        self.assertIsNotNone(obj.tracking_identifier)
        try:
            ActionItem.objects.get(
                reference_identifier=obj.tracking_identifier)
        except ObjectDoesNotExist:
            self.fail('ActionItem unexpectedly does not exist.')

        obj = TestModelWithAction.objects.create(
            subject_identifier=self.subject_identifier)
        try:
            ActionItem.objects.get(action_identifier=obj.action_identifier)
        except ObjectDoesNotExist:
            self.fail('ActionItem unexpectedly does not exist.')

    def test_action_type_update_from_action_classes(self):

        class MyAction(Action):
            name = 'my-action'
            display_name = 'my action'
            # model = 'edc_action_item.testmodelwithtrackingidentifier'

        class MyActionWithNextAction(Action):
            name = 'my-action-with-next-as-self'
            display_name = 'my action with next as self'
            # model = 'edc_action_item.testmodelwithtrackingidentifier'
            next_actions = [MyAction]

        class MyActionWithNextActionAsSelf(Action):
            name = 'my-action-with-next'
            display_name = 'my action with next'
            # model = 'edc_action_item.testmodelwithtrackingidentifier'
            next_actions = ['self']

        my_action = MyAction(
            subject_identifier=self.subject_identifier,
            tracking_identifier='tracking')

        try:
            action_item = ActionItem.objects.get(
                action_identifier=my_action.action_identifier)
        except ObjectDoesNotExist:
            self.fail('ActionItem unexpectedly does not exist')

        self.assertEqual(my_action.object, action_item)
        self.assertEqual(my_action.action_identifier,
                         action_item.action_identifier)
        self.assertEqual('tracking',
                         action_item.reference_identifier)
        self.assertEqual(my_action.action_type(),
                         action_item.action_type)
        self.assertEqual(my_action.action_type().name,
                         action_item.name)
        self.assertEqual(my_action.action_type().display_name,
                         action_item.display_name)
        self.assertEqual(my_action.action_type().model,
                         action_item.reference_model)
        self.assertIsNone(action_item.parent_action_item_id)
        self.assertIsNone(action_item.parent_model)
        self.assertIsNone(action_item.parent_reference_identifier)

        class MyActionWithModel(Action):
            name = 'my-action'
            display_name = 'my action'
            model = 'edc_action_item.TestModelWithoutMixin'

        obj = TestModelWithoutMixin.objects.create(
            subject_identifier=self.subject_identifier,
            tracking_identifier='tracking')
        self.assertRaises(
            ActionFieldError, MyActionWithModel, model_obj=obj)

        class MyActionWithCorrectModel(Action):
            name = 'my-action'
            display_name = 'my action'
            model = 'edc_action_item.TestModelWithAction'

        obj = TestModelWithAction.objects.create(
            subject_identifier=self.subject_identifier,
            tracking_identifier='tracking')
        my_action = MyActionWithCorrectModel(model_obj=obj)

        self.assertIsNotNone(my_action.model)
        self.assertEqual(my_action.action_type().model,
                         my_action.model)
        self.assertEqual(my_action.model,
                         my_action.object.reference_model)
