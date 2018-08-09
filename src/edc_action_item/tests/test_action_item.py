from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag
from edc_constants.constants import NEW, OPEN

from ..action import Action, ActionError, REFERENCE_MODEL_ERROR_CODE
from ..forms import ActionItemForm
from ..models import ActionItem, SubjectDoesNotExist
from ..models import ActionType
from ..site_action_items import site_action_items
from .action_items import FormZeroAction, FormOneAction, FormTwoAction
from .models import SubjectIdentifierModel
from .models import TestModelWithAction
from .models import FormOne, FormTwo


class TestActionItem(TestCase):

    def setUp(self):
        self.subject_identifier_model = ActionItem.subject_identifier_model
        ActionItem.subject_identifier_model = 'edc_action_item.subjectidentifiermodel'
        self.subject_identifier = '12345'
        SubjectIdentifierModel.objects.create(
            subject_identifier=self.subject_identifier)
        site_action_items.registry = {}
        site_action_items.register(FormZeroAction)
        FormZeroAction.action_type()
        self.action_type = ActionType.objects.get(name=FormZeroAction.name)

    def tearDown(self):
        ActionItem.subject_identifier_model = self.subject_identifier_model

#     def test_identifier_unique(self):
#         ids = []
#         for _ in range(0, 10000):
#             ids.append(ActionIdentifier().identifier)
#         self.assertEqual(len(ids), len(list(set(ids))))
#         pprint([obj.identifier for obj in ActionIdentifier().model_cls.objects.all()])

    def test_creates(self):
        obj = ActionItem.objects.create(
            subject_identifier=self.subject_identifier,
            action_type=self.action_type,
            reference_model='edc_action_item.testmodel')
        self.assertTrue(obj.action_identifier.startswith('AC'))
        self.assertEqual(obj.status, NEW)
        self.assertIsNotNone(obj.report_datetime)

    def test_create_requires_existing_subject(self):
        self.assertRaises(
            SubjectDoesNotExist,
            ActionItem.objects.create)

    def test_attrs(self):
        site_action_items.register(FormOneAction)
        site_action_items.register(FormTwoAction)
        form_one = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        form_two = FormTwo.objects.create(
            subject_identifier=self.subject_identifier,
            form_one=form_one)
        action_item_one = ActionItem.objects.get(
            action_identifier=form_one.action_identifier)
        action_item_two = ActionItem.objects.get(
            action_identifier=form_two.action_identifier)

        self.assertEqual(
            action_item_two.action_cls,
            site_action_items.get(action_item_two.action_type.name))
        self.assertTrue(action_item_two.parent)
        self.assertTrue(action_item_two.identifier)
        self.assertTrue(str(action_item_two))
        self.assertTrue(action_item_two.reference)
        self.assertTrue(action_item_two.parent_reference)
        self.assertIsNone(action_item_one.parent_reference)
        self.assertIsNone(action_item_one.parent)
        self.assertIsNone(action_item_one.parent_reference_model)

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

    def test_changes_action_item_status_from_new_to_open_on_edit(self):

        action_type = ActionType.objects.get(name=FormZeroAction.name)

        obj = ActionItem.objects.create(
            subject_identifier=self.subject_identifier,
            action_type=action_type)
        data = obj.__dict__
        data.update(action_type=obj.action_type.id)
        data['status'] = NEW
        form = ActionItemForm(data=obj.__dict__, instance=obj)
        form.is_valid()
        self.assertNotIn('status', form.errors)
        self.assertEqual(form.cleaned_data.get('status'), OPEN)

    def test_action_type_update_from_action_classes(self):

        class MyAction(Action):
            name = 'my-action'
            display_name = 'my action'
            reference_model = 'edc_action_item.reference'

        class MyActionWithNextAction(Action):
            name = 'my-action-with-next-as-self'
            display_name = 'my action with next as self'
            next_actions = [MyAction]
            reference_model = 'edc_action_item.reference'

        class MyActionWithNextActionAsSelf(Action):
            name = 'my-action-with-next'
            display_name = 'my action with next'
            next_actions = ['self']
            reference_model = 'edc_action_item.reference'

        site_action_items.register(MyAction)
        site_action_items.register(MyActionWithNextAction)
        site_action_items.register(MyActionWithNextActionAsSelf)
        my_action = MyAction(
            subject_identifier=self.subject_identifier)

        try:
            action_item = ActionItem.objects.get(
                action_identifier=my_action.action_identifier)
        except ObjectDoesNotExist:
            self.fail('ActionItem unexpectedly does not exist')

        self.assertEqual(my_action.action_item_obj, action_item)
        self.assertEqual(my_action.action_identifier,
                         action_item.action_identifier)
        self.assertEqual(my_action.action_type(),
                         action_item.action_type)
        self.assertEqual(my_action.action_type().reference_model,
                         action_item.reference_model)
        self.assertIsNone(action_item.parent_action_item_id)
        self.assertIsNone(action_item.parent_reference_model)
        self.assertIsNone(action_item.parent_reference_identifier)

        class MyActionWithIncorrectModel(Action):
            name = 'my-action2'
            display_name = 'my action'
            reference_model = 'edc_action_item.TestModelWithAction'
        site_action_items.register(MyActionWithIncorrectModel)

        with self.assertRaises(ActionError) as cm:
            TestModelWithAction.objects.create(
                subject_identifier=self.subject_identifier,
                action_identifier=action_item.action_identifier)
        self.assertEqual(cm.exception.code, REFERENCE_MODEL_ERROR_CODE)

    def test_action_type_updates(self):

        class MyAction(Action):
            name = 'my-action3'
            display_name = 'original display_name'
            reference_model = 'edc_action_item.FormOne'
        site_action_items.register(MyAction)
        MyAction(
            subject_identifier=self.subject_identifier)
        action_type = ActionType.objects.get(name='my-action3')
        self.assertEqual(action_type.display_name, 'original display_name')

        MyAction._updated_action_type = False
        MyAction.display_name = 'changed display_name'

        MyAction(
            subject_identifier=self.subject_identifier)
        action_type = ActionType.objects.get(name='my-action3')
        self.assertEqual(action_type.display_name, 'changed display_name')
