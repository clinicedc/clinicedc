from django.core.exceptions import ObjectDoesNotExist
from django.db.models.deletion import ProtectedError
from django.test import TestCase, tag
from edc_action_item.tests.action_items import FormTwoAction, FormOneAction
from edc_constants.constants import CLOSED, NEW
from uuid import uuid4

from ..action import ActionItemGetter, RelatedReferenceObjectDoesNotExist
from ..action import ActionItemGetterError
from ..get_action_type import get_action_type
from ..models import ActionItem, ActionType
from ..site_action_items import site_action_items
from .action_items import FormZeroAction, FormThreeAction, register_actions
from .models import SubjectIdentifierModel, FormOne, FormTwo


class TestActionItemGetter(TestCase):

    def setUp(self):
        register_actions()
        self.subject_identifier_model = ActionItem.subject_identifier_model
        ActionItem.subject_identifier_model = (
            'edc_action_item.subjectidentifiermodel')
        self.subject_identifier = '12345'
        SubjectIdentifierModel.objects.create(
            subject_identifier=self.subject_identifier)
        # force create action types
        for action_cls in site_action_items.registry.values():
            get_action_type(action_cls)

    def test_init(self):
        # ActionItem does not exist
        self.assertRaises(
            ObjectDoesNotExist,
            ActionItemGetter,
            FormZeroAction,
            subject_identifier=self.subject_identifier)
        # Action class creates ActionItem
        action = FormZeroAction(subject_identifier=self.subject_identifier)
        # ActionItem exists
        try:
            ActionItemGetter(
                FormZeroAction,
                subject_identifier=self.subject_identifier,
                action_identifier=action.action_identifier)
        except ObjectDoesNotExist:
            self.fail('Action item unexpectedly does not exist')

    def test_getter_finds_action_item_with_action_identifier(self):
        """Assert getter finds but does not create an
        action item if given and action_identifier.
        """
        action_type = ActionType.objects.get(name='submit-form-zero')
        obj = ActionItem.objects.create(
            subject_identifier=self.subject_identifier,
            action_type=action_type)
        getter = ActionItemGetter(
            FormZeroAction,
            action_identifier=obj.action_identifier,
            subject_identifier=self.subject_identifier)
        self.assertEqual(
            getter.action_item.action_identifier,
            obj.action_identifier)
        self.assertEqual(1, ActionItem.objects.filter(
            subject_identifier=self.subject_identifier,
            action_type=action_type).count())

    def test_getter_raises_if_no_action_item_but_action_identifier(self):
        """Assert getter raises if given an action_identifier
        for an action that does not exist.
        """
        action_type = ActionType.objects.get(name='submit-form-zero')
        obj = ActionItem.objects.create(
            subject_identifier=self.subject_identifier,
            action_type=action_type)
        action_identifier = obj.action_identifier
        obj.delete()
        self.assertRaises(
            ObjectDoesNotExist,
            ActionItemGetter,
            FormZeroAction,
            action_identifier=action_identifier,
            subject_identifier=self.subject_identifier)

    def test_getter_raises_if_expects_related_reference_obj_to_exist(self):
        """Assert a related reference object should have created
        the action item.
        """
        self.assertRaises(
            ObjectDoesNotExist,
            ActionItemGetter,
            FormTwoAction,
            subject_identifier=self.subject_identifier)

    def test_with_related_model_and_delete(self):
        """Assert a reference model on delete resets its action and
        cleans up next actions.
        """
        # create reference instance
        form_one_obj = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        action_identifier = form_one_obj.action_identifier

        # reference instance closes it's own action item
        ActionItem.objects.get(
            action_identifier=form_one_obj.action_identifier,
            action_type__name=FormOneAction.name,
            status=CLOSED)
        # reference instance creates next actions
        ActionItem.objects.get(
            action_type__name=FormTwoAction.name,
            status=NEW)

        # oops, parent got deleted
        FormOne.objects.all().delete()

        # form one action item is reset
        ActionItem.objects.get(
            action_identifier=form_one_obj.action_identifier,
            action_type__name=FormOneAction.name,
            status=NEW)

        # next actions are deleted
        # see the signal
        self.assertRaises(
            ObjectDoesNotExist,
            ActionItem.objects.get,
            parent_action_identifier=form_one_obj.action_identifier,
            action_type__name=FormTwoAction.name)

        # getter raises since FormTwoAction no longer exists
        # since related reference (FormOne) was deleted.
        self.assertRaises(
            ObjectDoesNotExist,
            ActionItemGetter,
            FormTwoAction,
            subject_identifier=self.subject_identifier,
            parent_action_identifier=action_identifier,
            related_action_identifier=action_identifier)

    def test_with_related_model_and_delete2(self):
        """Assert a "next" reference model on delete resets
        its action.
        """

        # create reference instance
        form_one_obj = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        action_identifier = form_one_obj.action_identifier

        # create next reference instance
        form_two_obj = FormTwo.objects.create(
            subject_identifier=self.subject_identifier,
            form_one=form_one_obj)

        # protected error keeps the sequence safe
        self.assertRaises(
            ProtectedError,
            FormOne.objects.all().delete)

        # now delete form two
        form_two_obj.delete()

        # assert form two action item is reset
        action_item = ActionItem.objects.get(
            action_identifier=form_two_obj.action_identifier,
            action_type__name=FormTwoAction.name,
            status=NEW)

        # assert getter finds the existing new (and just reset)
        # form two action item.
        self.assertEqual(
            action_item.pk,
            ActionItemGetter(
                FormTwoAction,
                subject_identifier=self.subject_identifier,
                parent_action_identifier=action_identifier,
                related_action_identifier=action_identifier).action_item.pk)

    def test_reference_values_and_related_pk(self):

        form_one = FormOne.objects.create(
            subject_identifier=self.subject_identifier)

        self.assertIsNotNone(form_one.action_identifier)

        # FormTwo finds 'submit-form-two' action item
        form_two = FormTwo.objects.create(
            subject_identifier=self.subject_identifier,
            form_one=form_one)

        self.assertEqual(
            form_one.action_identifier,
            form_two.parent_action_identifier)

        self.assertEqual(
            form_one.action_identifier,
            form_two.related_action_identifier)

        self.assertEqual(
            form_one.pk,
            form_two.form_one_id)

    def test_get_bad_action_identifier(self):
        self.assertRaises(
            ObjectDoesNotExist,
            ActionItemGetter,
            FormZeroAction,
            subject_identifier=self.subject_identifier,
            action_identifier=uuid4())

    def test_get_on_multiple_parents(self):
        # create 3 parents
        parent1 = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        parent2 = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        parent3 = FormOne.objects.create(
            subject_identifier=self.subject_identifier)

        # parent2 creates 1 child action item
        self.assertEqual(ActionItem.objects.filter(
            linked_to_reference=False,
            parent_action_identifier=parent2.action_identifier,
            action_type__name=get_action_type(FormTwo.get_action_cls()).name).count(), 1)
        self.assertEqual(ActionItem.objects.filter(
            linked_to_reference=False,
            related_action_identifier=parent2.action_identifier,
            action_type__name=get_action_type(FormTwo.get_action_cls()).name).count(), 1)

        # create "child2" with parent2
        child2 = FormTwo.objects.create(
            subject_identifier=self.subject_identifier,
            parent_action_identifier=parent2.action_identifier,
            form_one=parent2)
        # child2 links to action item created by parent2
        self.assertEqual(ActionItem.objects.filter(
            linked_to_reference=False,
            parent_action_identifier=parent2.action_identifier,
            action_type__name=get_action_type(FormTwo.get_action_cls()).name).count(), 0)
        # child2 creates new action_item where it is the parent and
        # parent2 is the related
        self.assertEqual(ActionItem.objects.filter(
            linked_to_reference=False,
            parent_action_identifier=child2.action_identifier,
            related_action_identifier=parent2.action_identifier,
            action_type__name=get_action_type(FormTwo.get_action_cls()).name).count(), 1)

        # so we have 4 form_two action_items
        # (3 created by parent2, 1 by child2)
        self.assertEqual(ActionItem.objects.filter(
            action_type__name=get_action_type(FormTwo.get_action_cls()).name).count(), 4)
        # of the 4,  we remain with 3 unlinked form_two action_items
        # (2 from by parent2, 1 from child2)
        self.assertEqual(ActionItem.objects.filter(
            linked_to_reference=False,
            action_type__name=get_action_type(FormTwo.get_action_cls()).name).count(), 3)

        # get child2_action_item using action_identifier
        # check attrs that link ActionItem to child2
        child2_action_item = ActionItem.objects.get(
            action_identifier=child2.action_identifier)
        self.assertEqual(child2_action_item.parent_action_identifier,
                         parent2.action_identifier)
        self.assertEqual(child2_action_item.related_action_identifier,
                         parent2.action_identifier)

        # get child2_action_item using the getter
        getter = ActionItemGetter(
            child2.get_action_cls(),
            subject_identifier=child2.subject_identifier,
            action_identifier=child2.action_identifier,
            parent_action_identifier=child2.parent_action_identifier,
            related_action_identifier=child2.related_action_identifier)
        self.assertEqual(getter.action_item.action_identifier,
                         child2.action_identifier)
        self.assertEqual(child2_action_item.parent_action_identifier,
                         parent2.action_identifier)
        self.assertEqual(child2_action_item.related_action_identifier,
                         parent2.action_identifier)

        # repeat for child1, child3
        FormTwo.objects.create(
            subject_identifier=self.subject_identifier,
            parent_action_identifier=parent1.action_identifier,
            form_one=parent1)
        FormTwo.objects.create(
            subject_identifier=self.subject_identifier,
            parent_action_identifier=parent3.action_identifier,
            form_one=parent3)

        # no ActionItems are available with parent_action_identifiers from
        # the original FormOne instances.
        self.assertEqual(ActionItem.objects.filter(
            action_type__name=get_action_type(FormTwo.get_action_cls()).name,
            parent_action_identifier__in=[
                parent1.action_identifier,
                parent2.action_identifier,
                parent3.action_identifier],
            linked_to_reference=False).count(), 0)

        # creating a child using any of the original parents
        # should fail because the child cannot create a new ActionItem
        # with form_one as parent
        self.assertRaises(
            RelatedReferenceObjectDoesNotExist,
            FormTwo.objects.create,
            subject_identifier=self.subject_identifier,
            parent_action_identifier=parent2.action_identifier,
            form_one=parent2)

    def test_gets_existing(self):
        # parent
        form_one = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        self.assertIsNotNone(form_one.action_identifier)

        # FormTwo finds 'submit-form-two' action item
        form_two = FormTwo.objects.create(
            subject_identifier=self.subject_identifier,
            related_action_identifier=form_one.action_identifier,
            parent_action_identifier=form_one.action_identifier,
            form_one=form_one)

        getter = ActionItemGetter(
            form_two.get_action_cls(),
            subject_identifier=form_two.subject_identifier,
            action_identifier=form_two.action_identifier,
            parent_action_identifier=form_one.action_identifier,
            related_action_identifier=form_one.action_identifier)

        self.assertEqual(getter.action_item.action_identifier,
                         form_two.action_identifier)

    def test_delete_on_multiple_parents(self):
        """Assert multpile actions does not confuse getter.
        """

        parent1 = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        parent2 = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        parent3 = FormOne.objects.create(
            subject_identifier=self.subject_identifier)

        getter = ActionItemGetter(
            FormOne.get_action_cls(),
            action_identifier=parent1.action_identifier,
            subject_identifier=self.subject_identifier)
        self.assertEqual(getter.action_item.status, CLOSED)

        getter = ActionItemGetter(
            FormOne.get_action_cls(),
            action_identifier=parent2.action_identifier,
            subject_identifier=self.subject_identifier)
        self.assertEqual(getter.action_item.status, CLOSED)

        getter = ActionItemGetter(
            FormOne.get_action_cls(),
            action_identifier=parent3.action_identifier,
            subject_identifier=self.subject_identifier)
        self.assertEqual(getter.action_item.status, CLOSED)

        parent2.delete()

        getter = ActionItemGetter(
            FormOne.get_action_cls(),
            action_identifier=parent1.action_identifier,
            subject_identifier=self.subject_identifier)
        self.assertEqual(getter.action_item.status, CLOSED)

        getter = ActionItemGetter(
            FormOne.get_action_cls(),
            action_identifier=parent2.action_identifier,
            subject_identifier=self.subject_identifier)
        self.assertEqual(getter.action_item.status, NEW)

        getter = ActionItemGetter(
            FormOne.get_action_cls(),
            action_identifier=parent3.action_identifier,
            subject_identifier=self.subject_identifier)
        self.assertEqual(getter.action_item.status, CLOSED)

    def test_no_action_identifier_and_no_subject_raises(self):

        self.assertRaises(
            ActionItemGetterError,
            ActionItemGetter, FormZeroAction,
            action_identifier=None, subject_identifier=None)

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
            parent_action_identifier=form_one_obj.action_identifier)

        self.assertEqual(
            getter.action_item.parent_action_identifier,
            form_one_obj.action_identifier)
