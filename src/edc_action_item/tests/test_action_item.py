from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag
from edc_constants.constants import NEW, OPEN

from ..action import Action, ActionError
from ..action_items import ReminderAction
from ..forms import ActionItemForm
from ..model_mixins import ActionClassNotDefined
from ..models import ActionItem, ActionItemUpdate, SubjectDoesNotExist, ActionType, ActionTypeError
from ..site_action_items import site_action_items
from .models import SubjectIdentifierModel, TestModelWithTrackingIdentifierButNoActionClass
from .models import TestModel, TestModelWithAction
from .models import TestModelWithoutMixin
from uuid import uuid4
from edc_action_item.tests.action_items import FormZeroAction


class TestActionItem(TestCase):

    def setUp(self):
        self.subject_identifier_model = ActionItem.subject_identifier_model
        ActionItem.subject_identifier_model = 'edc_action_item.subjectidentifiermodel'
        self.subject_identifier = '12345'
        SubjectIdentifierModel.objects.create(
            subject_identifier=self.subject_identifier)
        site_action_items.registry = {}
        site_action_items.register(ReminderAction)
        site_action_items.register(FormZeroAction)
        FormZeroAction.action_type()
        ReminderAction.action_type()
        self.action_type = ActionType.objects.get(name=FormZeroAction.name)

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

    def test_changes_status_from_new_to_open_on_edit(self):

        class MyAction(Action):
            name = 'a new action item'

        site_action_items.register(MyAction)
        MyAction.action_type()

        action_type = ActionType.objects.get(name=MyAction.name)

        obj = ActionItem.objects.create(
            subject_identifier=self.subject_identifier,
            action_type=action_type)
        ActionItemUpdate.objects.create(action_item=obj)
        ActionItemUpdate.objects.create(action_item=obj)
        ActionItemUpdate.objects.create(action_item=obj)
        data = obj.__dict__
        data.update(action_type=obj.action_type.id)
        data['status'] = NEW
        form = ActionItemForm(data=obj.__dict__, instance=obj)
        form.is_valid()
        self.assertNotIn('status', form.errors)
        self.assertEqual(form.cleaned_data.get('status'), OPEN)

    def test_action(self):

        class MyNonPrnAction(Action):
            name = 'prn_action1'
            model = None

        # create action
        site_action_items.register(MyNonPrnAction)
        action = MyNonPrnAction(subject_identifier=self.subject_identifier)
        self.assertIsNotNone(action.object)

        # create action but incorrect instantiate with a model instance
        class MyPrnActionMissingModel(Action):
            name = 'prn_action2'

        site_action_items.register(MyPrnActionMissingModel)
        model_obj = TestModel(subject_identifier='98765')
        self.assertRaises(
            SubjectDoesNotExist,
            MyPrnActionMissingModel, model_obj=model_obj)

        # create instance but instantiate with wrong model type
        class MyPrnActionWrongModel(Action):
            name = 'prn_action3'
            model = 'edc_action_item.formone'

        site_action_items.register(MyPrnActionWrongModel)
        model_obj = TestModel(subject_identifier=self.subject_identifier)
        self.assertRaises(
            ActionError,
            MyPrnActionWrongModel, model_obj=model_obj)

        # create instance but declare/instantiate with model class that has not
        # actions
        class MyPrnAction(Action):
            name = 'prn_action4'
            model = 'edc_action_item.TestModelWithTrackingIdentifierButNoActionClass'

        site_action_items.register(MyPrnAction)
        self.assertRaises(
            ActionClassNotDefined,
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

    @tag('9')
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

        site_action_items.register(MyAction)
        site_action_items.register(MyActionWithNextAction)
        site_action_items.register(MyActionWithNextActionAsSelf)
        tracking_identifier = str(uuid4())
        my_action = MyAction(
            subject_identifier=self.subject_identifier,
            tracking_identifier=tracking_identifier)

        try:
            action_item = ActionItem.objects.get(
                action_identifier=my_action.action_identifier)
        except ObjectDoesNotExist:
            self.fail('ActionItem unexpectedly does not exist')

        self.assertEqual(my_action.object, action_item)
        self.assertEqual(my_action.action_identifier,
                         action_item.action_identifier)
        self.assertEqual(tracking_identifier,
                         action_item.reference_identifier)
        self.assertEqual(my_action.action_type(),
                         action_item.action_type)
        self.assertEqual(my_action.action_type().model,
                         action_item.reference_model)
        self.assertIsNone(action_item.parent_action_item_id)
        self.assertIsNone(action_item.parent_model)
        self.assertIsNone(action_item.parent_reference_identifier)

        class MyActionWithModel(Action):
            name = 'my-action1'
            display_name = 'my action'
            model = 'edc_action_item.TestModelWithoutMixin'

        site_action_items.register(MyActionWithModel)
        obj = TestModelWithoutMixin.objects.create(
            subject_identifier=self.subject_identifier,
            tracking_identifier=tracking_identifier)
        self.assertRaises(
            ActionTypeError, MyActionWithModel, model_obj=obj)

        class MyActionWithCorrectModel(Action):
            name = 'my-action2'
            display_name = 'my action'
            model = 'edc_action_item.TestModelWithAction'
        site_action_items.register(MyActionWithCorrectModel)

        obj = TestModelWithAction.objects.create(
            subject_identifier=self.subject_identifier,
            tracking_identifier=tracking_identifier)
        my_action = MyActionWithCorrectModel(model_obj=obj)

        self.assertIsNotNone(my_action.model)
        self.assertEqual(my_action.action_type().model,
                         my_action.model)
        self.assertEqual(my_action.model,
                         my_action.object.reference_model)

    def test_action_type_updates(self):

        class MyAction(Action):
            name = 'my-action3'
            display_name = 'my action'
            model = 'edc_action_item.FormOne'
        site_action_items.register(MyAction)
        MyAction(
            subject_identifier=self.subject_identifier)
        action_type = ActionType.objects.get(name='my-action3')
        self.assertEqual(action_type.display_name, 'my action')

        MyAction._updated_action_type = False
        MyAction.display_name = 'my changed action'
        MyAction(
            subject_identifier=self.subject_identifier)
        action_type = ActionType.objects.get(name='my-action3')
        self.assertEqual(action_type.display_name, 'my changed action')
