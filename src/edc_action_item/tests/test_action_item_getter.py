from django.test import TestCase, tag
from edc_constants.constants import CLOSED, NEW
from uuid import uuid4

from ..action import ActionItemGetter, ActionItemObjectDoesNotExist
from ..action import ActionItemGetterError, RelatedReferenceModelDoesNotExist
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
            action_identifier=obj.action_identifier,
            subject_identifier=self.subject_identifier)
        self.assertEqual(
            getter.action_item.action_identifier,
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
            getter.action_item.action_identifier,
            obj.action_identifier)

    def test_raises_if_fk_attr_but_no_related_reference_model1(self):
        # parent
        form_one_obj = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        self.assertIsNotNone(form_one_obj.action_identifier)

        FormOne.objects.all().delete()
        # FormTwo finds 'submit-form-two' action item
        self.assertRaises(RelatedReferenceModelDoesNotExist,
                          FormTwo.objects.create,
                          subject_identifier=self.subject_identifier,
                          form_one=form_one_obj)

    def test_reference_values_and_related_pk(self):
        # parent
        form_one = FormOne.objects.create(
            subject_identifier=self.subject_identifier)

        self.assertIsNotNone(form_one.action_identifier)

        # FormTwo finds 'submit-form-two' action item
        form_two = FormTwo.objects.create(
            subject_identifier=self.subject_identifier,
            form_one=form_one)

        self.assertEqual(
            form_one.action_identifier,
            form_two.parent_reference_identifier)

        self.assertEqual(
            form_one.action_identifier,
            form_two.related_reference_identifier)

        self.assertEqual(
            form_one.pk,
            form_two.form_one_id)

    def test_get_bad_action_identifier(self):
        self.assertRaises(
            ActionItemObjectDoesNotExist,
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
            parent_reference_identifier=parent2.action_identifier,
            action_type__name=FormTwo.action_cls().action_type().name).count(), 1)
        self.assertEqual(ActionItem.objects.filter(
            linked_to_reference=False,
            related_reference_identifier=parent2.action_identifier,
            action_type__name=FormTwo.action_cls().action_type().name).count(), 1)

        # create "child2" with parent2
        child2 = FormTwo.objects.create(
            subject_identifier=self.subject_identifier,
            parent_reference_identifier=parent2.action_identifier,
            form_one=parent2)
        # child2 links to action item created by parent2
        self.assertEqual(ActionItem.objects.filter(
            linked_to_reference=False,
            parent_reference_identifier=parent2.action_identifier,
            action_type__name=FormTwo.action_cls().action_type().name).count(), 0)
        # child2 creates new action_item where it is the parent and
        # parent2 is the related
        self.assertEqual(ActionItem.objects.filter(
            linked_to_reference=False,
            parent_reference_identifier=child2.action_identifier,
            related_reference_identifier=parent2.action_identifier,
            action_type__name=FormTwo.action_cls().action_type().name).count(), 1)

        # so we have 4 form_two action_items
        # (3 created by parent2, 1 by child2)
        self.assertEqual(ActionItem.objects.filter(
            action_type__name=FormTwo.action_cls().action_type().name).count(), 4)
        # of the 4,  we remain with 3 unlinked form_two action_items
        # (2 from by parent2, 1 from child2)
        self.assertEqual(ActionItem.objects.filter(
            linked_to_reference=False,
            action_type__name=FormTwo.action_cls().action_type().name).count(), 3)

        # get child2_action_item using action_identifier
        # check attrs that link ActionItem to child2
        child2_action_item = ActionItem.objects.get(
            action_identifier=child2.action_identifier)
        self.assertEqual(child2_action_item.parent_reference_identifier,
                         parent2.action_identifier)
        self.assertEqual(child2_action_item.related_reference_identifier,
                         parent2.action_identifier)

        # get child2_action_item using the getter
        getter = ActionItemGetter(
            child2.action_cls(),
            subject_identifier=child2.subject_identifier,
            action_identifier=child2.action_identifier,
            parent_reference_identifier=child2.parent_reference_identifier,
            related_reference_identifier=child2.related_reference_identifier)
        self.assertEqual(getter.action_item.action_identifier,
                         child2.action_identifier)
        self.assertEqual(child2_action_item.parent_reference_identifier,
                         parent2.action_identifier)
        self.assertEqual(child2_action_item.related_reference_identifier,
                         parent2.action_identifier)

        # repeat for child1, child3
        FormTwo.objects.create(
            subject_identifier=self.subject_identifier,
            parent_reference_identifier=parent1.action_identifier,
            form_one=parent1)
        FormTwo.objects.create(
            subject_identifier=self.subject_identifier,
            parent_reference_identifier=parent3.action_identifier,
            form_one=parent3)

        # no ActionItems are available with parent_reference_identifiers from
        # the original FormOne instances.
        self.assertEqual(ActionItem.objects.filter(
            action_type__name=FormTwo.action_cls().action_type().name,
            parent_reference_identifier__in=[
                parent1.action_identifier,
                parent2.action_identifier,
                parent3.action_identifier],
            linked_to_reference=False).count(), 0)

        # creating a child using any of the original parents
        # should fail because the child cannot create a new ActionItem
        # with form_one as parent
        self.assertRaises(
            ActionItemObjectDoesNotExist,
            FormTwo.objects.create,
            subject_identifier=self.subject_identifier,
            parent_reference_identifier=parent2.action_identifier,
            form_one=parent2)

    def test_gets_existing(self):
        # parent
        form_one = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        self.assertIsNotNone(form_one.action_identifier)

        # FormTwo finds 'submit-form-two' action item
        form_two = FormTwo.objects.create(
            subject_identifier=self.subject_identifier,
            related_reference_identifier=form_one.action_identifier,
            parent_reference_identifier=form_one.action_identifier,
            form_one=form_one)

        getter = ActionItemGetter(
            form_two.action_cls(),
            subject_identifier=form_two.subject_identifier,
            action_identifier=form_two.action_identifier,
            parent_reference_identifier=form_one.action_identifier,
            related_reference_identifier=form_one.action_identifier)

        self.assertEqual(getter.action_item.action_identifier,
                         form_two.action_identifier)

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
            parent_reference_identifier=form_one_obj.action_identifier)

        self.assertEqual(
            getter.action_item.parent_reference_identifier,
            form_one_obj.action_identifier)
