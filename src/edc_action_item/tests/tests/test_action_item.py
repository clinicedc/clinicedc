from django.core.exceptions import ObjectDoesNotExist
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from edc_constants.constants import CLOSED, NEW, OPEN

from edc_action_item.action import Action
from edc_action_item.create_or_update_action_type import create_or_update_action_type
from edc_action_item.forms import ActionItemForm
from edc_action_item.get_action_type import get_action_type
from edc_action_item.models import ActionItem, ActionType, SubjectDoesNotExist
from edc_action_item.site_action_items import site_action_items

from ..action_items import FormOneAction, FormThreeAction, FormTwoAction, FormZeroAction
from ..models import FormOne, FormThree, FormTwo, TestModelWithAction
from ..test_case_mixin import TestCaseMixin


class TestActionItem(TestCaseMixin, TestCase):
    def setUp(self):
        self.subject_identifier = self.fake_enroll()
        site_action_items.registry = {}
        site_action_items.register(FormZeroAction)
        get_action_type(FormZeroAction)
        self.action_type = ActionType.objects.get(name=FormZeroAction.name)

    def test_creates(self):
        obj = ActionItem.objects.create(
            subject_identifier=self.subject_identifier,
            action_type=self.action_type,
            reference_model="edc_action_item.testmodel",
        )
        self.assertTrue(obj.action_identifier.startswith("AC"))
        self.assertEqual(obj.status, NEW)
        self.assertIsNotNone(obj.report_datetime)

    def test_create_requires_existing_subject(self):
        self.assertRaises(SubjectDoesNotExist, ActionItem.objects.create)

    def test_attrs(self):
        site_action_items.register(FormOneAction)
        site_action_items.register(FormTwoAction)
        site_action_items.register(FormThreeAction)
        form_one = FormOne.objects.create(subject_identifier=self.subject_identifier)
        form_one.refresh_from_db()
        form_two = FormTwo.objects.create(
            subject_identifier=self.subject_identifier, form_one=form_one
        )
        form_two.refresh_from_db()
        action_item_one = ActionItem.objects.get(action_identifier=form_one.action_identifier)
        action_item_two = ActionItem.objects.get(action_identifier=form_two.action_identifier)

        self.assertEqual(
            action_item_two.action_cls,
            site_action_items.get(action_item_two.action_type.name),
        )
        self.assertTrue(action_item_two.identifier)
        self.assertTrue(str(action_item_two))
        self.assertTrue(action_item_two.parent_action_item)
        self.assertIsNone(action_item_one.parent_action_item)

    def test_identifier_not_changed(self):
        site_action_items.registry = {}
        site_action_items.register(FormOneAction)
        get_action_type(FormOneAction)
        action_type = ActionType.objects.get(name=FormOneAction.name)
        obj = ActionItem.objects.create(
            subject_identifier=self.subject_identifier, action_type=action_type
        )
        action_identifier = obj.action_identifier
        obj.save()
        try:
            ActionItem.objects.get(action_identifier=action_identifier)
        except ObjectDoesNotExist:
            self.fail("ActionItem unexpectedly does not exist")

    def test_changes_action_item_status_from_new_to_open_on_edit(self):

        action_type = ActionType.objects.get(name=FormZeroAction.name)

        obj = ActionItem.objects.create(
            subject_identifier=self.subject_identifier, action_type=action_type
        )
        data = obj.__dict__
        data.update(action_type=obj.action_type.id)
        data["status"] = NEW
        form = ActionItemForm(data=obj.__dict__, instance=obj)
        form.is_valid()
        self.assertNotIn("status", form.errors)
        self.assertEqual(form.cleaned_data.get("status"), OPEN)

    def test_action_type_update_from_action_classes(self):
        class MyAction(Action):
            name = "my-action"
            display_name = "my action"
            reference_model = "edc_action_item.reference"

        class MyActionWithNextAction(Action):
            name = "my-action-with-next-as-self"
            display_name = "my action with next as self"
            next_actions = [MyAction]
            reference_model = "edc_action_item.reference"

        class MyActionWithNextActionAsSelf(Action):
            name = "my-action-with-next"
            display_name = "my action with next"
            next_actions = ["self"]
            reference_model = "edc_action_item.reference"

        site_action_items.register(MyAction)
        site_action_items.register(MyActionWithNextAction)
        site_action_items.register(MyActionWithNextActionAsSelf)
        my_action = MyAction(subject_identifier=self.subject_identifier)

        try:
            action_item = ActionItem.objects.get(action_identifier=my_action.action_identifier)
        except ObjectDoesNotExist:
            self.fail("ActionItem unexpectedly does not exist")

        self.assertEqual(my_action.action_item, action_item)
        self.assertEqual(my_action.action_identifier, action_item.action_identifier)
        self.assertEqual(get_action_type(my_action), action_item.action_type)
        self.assertEqual(
            get_action_type(my_action).reference_model, action_item.reference_model
        )
        self.assertIsNone(action_item.parent_action_item_id)

        class MyActionWithIncorrectModel(Action):
            name = "my-action2"
            display_name = "my action 2"
            reference_model = "edc_action_item.TestModelWithAction"

        site_action_items.register(MyActionWithIncorrectModel)

        TestModelWithAction.objects.create(subject_identifier=self.subject_identifier)
        self.assertRaises(
            ObjectDoesNotExist,
            TestModelWithAction.objects.create,
            subject_identifier=self.subject_identifier,
            action_identifier="blahblah",
        )

    def test_action_type_updates(self):
        class MyAction(Action):
            name = "my-action3"
            display_name = "original display_name"
            reference_model = "edc_action_item.FormOne"

        site_action_items.register(MyAction)
        MyAction(subject_identifier=self.subject_identifier)
        action_type = ActionType.objects.get(name="my-action3")
        self.assertEqual(action_type.display_name, "original display_name")

        site_action_items.registry = {}
        MyAction.display_name = "changed display_name"
        site_action_items.register(MyAction)
        create_or_update_action_type(**MyAction.as_dict())
        MyAction(subject_identifier=self.subject_identifier)
        action_type = ActionType.objects.get(name="my-action3")
        self.assertEqual(action_type.display_name, "changed display_name")

    def test_delete_child_and_parent_recreates(self):
        site_action_items.register(FormOneAction)
        site_action_items.register(FormTwoAction)
        site_action_items.register(FormThreeAction)
        form_one_action = FormOneAction(subject_identifier=self.subject_identifier)
        form_one = FormOne.objects.create(
            subject_identifier=self.subject_identifier,
            action_identifier=form_one_action.action_identifier,
        )
        action_item = ActionItem.objects.get(action_type__name=FormTwoAction.name)
        action_item.delete()
        action_item = ActionItem.objects.get(action_type__name=FormThreeAction.name)
        action_item.delete()
        # assert deleted actions are recreated
        self.assertEqual(ActionItem.objects.all().count(), 3)
        # assert two are parents of form one
        self.assertEqual(
            ActionItem.objects.filter(
                parent_action_item__action_identifier=form_one.action_identifier
            ).count(),
            2,
        )

    def test_delete2(self):
        site_action_items.register(FormOneAction)
        site_action_items.register(FormTwoAction)
        site_action_items.register(FormThreeAction)
        form_one_action = FormOneAction(subject_identifier=self.subject_identifier)
        form_one = FormOne.objects.create(
            subject_identifier=self.subject_identifier,
            action_identifier=form_one_action.action_identifier,
        )

        # delete form one
        form_one.delete()
        # assert resets action item
        action_item = ActionItem.objects.get(action_type__name=FormOneAction.name, status=NEW)

        # assert cleans up child action items
        self.assertRaises(
            ObjectDoesNotExist,
            ActionItem.objects.get,
            action_type__name=FormTwoAction.name,
        )
        self.assertRaises(
            ObjectDoesNotExist,
            ActionItem.objects.get,
            action_type__name=FormThreeAction.name,
        )

        # assert can delete form one action
        action_item.delete()

    def test_delete3(self):
        """Assert cannot delete action item if reference
        object exists.
        """
        site_action_items.register(FormOneAction)
        site_action_items.register(FormTwoAction)
        site_action_items.register(FormThreeAction)
        form_one_action = FormOneAction(subject_identifier=self.subject_identifier)
        FormOne.objects.create(
            subject_identifier=self.subject_identifier,
            action_identifier=form_one_action.action_identifier,
        )

        action_item = ActionItem.objects.get(action_type__name=FormOneAction.name)

        self.assertRaises(ProtectedError, action_item.delete)

    def test_new(self):
        site_action_items.register(FormOneAction)
        site_action_items.register(FormTwoAction)
        site_action_items.register(FormThreeAction)

        form_one_action = FormOneAction(subject_identifier=self.subject_identifier)

        self.assertEqual(form_one_action.action_item.status, NEW)

    def test_close_on_create(self):
        site_action_items.register(FormOneAction)
        site_action_items.register(FormTwoAction)
        site_action_items.register(FormThreeAction)

        form_one_action = FormOneAction(subject_identifier=self.subject_identifier)

        self.assertEqual(form_one_action.action_item.status, NEW)

        form_one = FormOne.objects.create(
            subject_identifier=self.subject_identifier,
            action_identifier=form_one_action.action_identifier,
        )

        self.assertEqual(form_one.action_item.status, CLOSED)

    def test_all_closed_on_create(self):
        site_action_items.register(FormOneAction)
        site_action_items.register(FormTwoAction)
        site_action_items.register(FormThreeAction)

        form_one_action = FormOneAction(subject_identifier=self.subject_identifier)

        form_one = FormOne.objects.create(
            subject_identifier=self.subject_identifier,
            action_identifier=form_one_action.action_identifier,
        )

        form_two = FormTwo.objects.create(
            subject_identifier=self.subject_identifier, form_one=form_one
        )

        form_three = FormThree.objects.create(subject_identifier=self.subject_identifier)

        self.assertEqual(form_one.action_item.status, CLOSED)
        self.assertEqual(form_two.action_item.status, CLOSED)
        self.assertEqual(form_three.action_item.status, CLOSED)

    def test_detects_change(self):
        site_action_items.register(FormOneAction)
        site_action_items.register(FormTwoAction)
        site_action_items.register(FormThreeAction)

        form_one_action = FormOneAction(subject_identifier=self.subject_identifier)
        form_one = FormOne.objects.create(
            subject_identifier=self.subject_identifier,
            action_identifier=form_one_action.action_identifier,
        )

        form_one.f1 = "blah"
        form_one.save()

        form_one.refresh_from_db()

        self.assertIsNotNone(form_one.action.reference_obj_has_changed)

    def test_reopens_children_on_change(self):
        site_action_items.register(FormOneAction)
        site_action_items.register(FormTwoAction)
        site_action_items.register(FormThreeAction)

        form_one_action = FormOneAction(subject_identifier=self.subject_identifier)
        form_one = FormOne.objects.create(
            subject_identifier=self.subject_identifier,
            action_identifier=form_one_action.action_identifier,
        )
        form_two = FormTwo.objects.create(
            subject_identifier=self.subject_identifier, form_one=form_one
        )
        form_three = FormThree.objects.create(subject_identifier=self.subject_identifier)

        form_one.f1 = "blah"
        form_one.save()

        form_one.refresh_from_db()
        form_two.refresh_from_db()
        form_three.refresh_from_db()

        self.assertEqual(form_two.action_item.status, OPEN)
        self.assertEqual(form_three.action_item.status, OPEN)
        self.assertEqual(form_one.action_item.status, CLOSED)
