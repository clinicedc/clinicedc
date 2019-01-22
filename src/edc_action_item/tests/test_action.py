from django.test import TestCase, tag
from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import CLOSED, NEW, YES, NO

from ..get_action_type import get_action_type
from ..models import ActionItem, ActionType
from ..site_action_items import site_action_items
from .action_items import FormOneAction, FormTwoAction, FormThreeAction, FormZeroAction
from .action_items import SingletonAction, register_actions, FormFourAction
from .models import FormZero, FormOne, FormTwo
from .models import FormFour, FormThree, SubjectIdentifierModel
from edc_action_item.helpers import ActionItemHelper


class TestAction(TestCase):
    def setUp(self):
        register_actions()
        self.subject_identifier_model = ActionItem.subject_identifier_model
        ActionItem.subject_identifier_model = "edc_action_item.subjectidentifiermodel"
        self.subject_identifier = "12345"
        SubjectIdentifierModel.objects.create(
            subject_identifier=self.subject_identifier
        )
        self.assertEqual(0, ActionType.objects.all().count())
        self.assertIn(FormOneAction.name, site_action_items.registry)
        self.assertIn(FormTwoAction.name, site_action_items.registry)
        self.assertIn(FormThreeAction.name, site_action_items.registry)

    def tearDown(self):
        ActionItem.subject_identifier_model = self.subject_identifier_model

    def test_str(self):
        action = FormZeroAction(subject_identifier=self.subject_identifier)
        self.assertTrue(str(action))

    def test_create_or_update_action_type(self):
        site_action_items.updated_action_types = False
        site_action_items.create_or_update_action_types()
        self.assertGreater(len(site_action_items.registry), 0)
        self.assertEqual(
            ActionType.objects.all().count(), len(site_action_items.registry)
        )
        self.assertTrue(site_action_items.updated_action_types)

        site_action_items.create_or_update_action_types()
        self.assertGreater(len(site_action_items.registry), 0)
        self.assertEqual(
            ActionType.objects.all().count(), len(site_action_items.registry)
        )

    def test_creates_own_action0(self):
        """Asserts a form creates it's action item.
        """
        form_zero = FormZero.objects.create(subject_identifier=self.subject_identifier)
        try:
            ActionItem.objects.get(action_identifier=form_zero.action_identifier)
        except ObjectDoesNotExist:
            self.fail("Action item unexpectedly does not exist")
        for name in ["submit-form-zero"]:
            with self.subTest(name=name):
                try:
                    ActionItem.objects.get(
                        subject_identifier=self.subject_identifier,
                        action_type__name=name,
                    )
                except ObjectDoesNotExist:
                    self.fail("Action item unexpectedly does not exist.")
        self.assertEqual(
            ActionItem.objects.filter(
                subject_identifier=self.subject_identifier
            ).count(),
            1,
        )

    def test_check_attrs_for_own_action0(self):
        """Test when model creates action.
        """
        obj = FormZero.objects.create(subject_identifier=self.subject_identifier)
        action_type = get_action_type(site_action_items.get(FormZero.action_name))
        action_item = ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            action_type__name="submit-form-zero",
        )
        self.assertEqual(action_item.subject_identifier, obj.subject_identifier)
        self.assertEqual(action_item.action_identifier, obj.action_identifier)
        self.assertEqual(action_item.action_identifier, obj.action_identifier)
        self.assertEqual(action_item.reference_model, obj._meta.label_lower)
        self.assertTrue(action_item.linked_to_reference)
        self.assertIsNone(action_item.related_action_item)
        self.assertIsNone(action_item.related_reference_model)
        self.assertIsNone(action_item.parent_action_item)
        # self.assertIsNone(action_item.parent_reference_model)
        self.assertIsNone(action_item.parent_action_item)
        self.assertEqual(action_item.action_type, action_type)

    def test_check_attrs_for_own_action1(self):
        """Test when action creates model.
        """
        obj = FormZero.objects.create(subject_identifier=self.subject_identifier)
        action = FormZeroAction(action_identifier=obj.action_identifier)
        self.assertEqual(action.subject_identifier, obj.subject_identifier)
        self.assertEqual(action.action_identifier, obj.action_identifier)
        self.assertEqual(action.action_identifier, obj.action_identifier)
        self.assertEqual(action.reference_model, obj._meta.label_lower)
        self.assertTrue(action.linked_to_reference)
        self.assertIsNone(action.related_action_item)
        self.assertIsNone(action.related_reference_model)
        self.assertIsNone(action.parent_action_item)
        action_type = get_action_type(site_action_items.get(FormZero.action_name))
        self.assertEqual(get_action_type(action), action_type)

    def test_check_attrs_for_form_one_next_action(self):

        form_one = FormOne.objects.create(subject_identifier=self.subject_identifier)

        action_type_two = get_action_type(site_action_items.get(FormTwo.action_name))

        action_item_one = ActionItem.objects.get(
            action_identifier=form_one.action_identifier, status=CLOSED
        )
        action_item_two = ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            action_type__name="submit-form-two",
            status=NEW,
        )
        form_one = FormOne.objects.get(id=form_one.id)

        self.assertEqual(
            action_item_two.subject_identifier, form_one.subject_identifier
        )
        self.assertNotEqual(
            action_item_two.action_identifier, form_one.action_identifier
        )
        self.assertEqual(action_item_two.reference_model, FormTwo._meta.label_lower)
        self.assertEqual(action_item_two.related_action_item, form_one.action_item)
        self.assertEqual(
            action_item_two.related_reference_model, FormOne._meta.label_lower
        )
        self.assertEqual(action_item_two.parent_action_item, form_one.action_item)
        self.assertEqual(
            action_item_two.parent_action_item.reference_model,
            action_item_one.reference_model,
        )
        self.assertEqual(action_item_two.parent_action_item, action_item_one)
        self.assertEqual(get_action_type(action_item_two.action_cls), action_type_two)

    def test_does_not_duplicate_own_action_on_save(self):
        obj = FormZero.objects.create(subject_identifier=self.subject_identifier)
        obj.save()
        for name in ["submit-form-zero"]:
            with self.subTest(name=name):
                try:
                    ActionItem.objects.get(
                        subject_identifier=self.subject_identifier,
                        action_type__name=name,
                    )
                except ObjectDoesNotExist:
                    self.fail("Action item unexpectedly does not exist.")
        self.assertEqual(
            ActionItem.objects.filter(
                subject_identifier=self.subject_identifier
            ).count(),
            1,
        )

    def test_creates_own_action1(self):
        obj = FormOne.objects.create(subject_identifier=self.subject_identifier)
        try:
            obj = ActionItem.objects.get(action_identifier=obj.action_identifier)
        except ObjectDoesNotExist:
            self.fail("Action item unexpectedly does not exist")
        for name in ["submit-form-one", "submit-form-two", "submit-form-three"]:
            with self.subTest(name=name):
                try:
                    ActionItem.objects.get(
                        subject_identifier=self.subject_identifier,
                        action_type__name=name,
                    )
                except ObjectDoesNotExist:
                    self.fail("Action item unexpectedly does not exist.")
        self.assertEqual(
            ActionItem.objects.filter(
                subject_identifier=self.subject_identifier
            ).count(),
            3,
        )

    def test_does_not_duplicate_own_actions_on_save(self):
        obj = FormOne.objects.create(subject_identifier=self.subject_identifier)
        self.assertEqual(
            ActionItem.objects.filter(
                subject_identifier=self.subject_identifier
            ).count(),
            3,
        )
        obj.save()
        self.assertEqual(
            ActionItem.objects.filter(
                subject_identifier=self.subject_identifier
            ).count(),
            3,
        )
        for name in ["submit-form-one", "submit-form-two", "submit-form-three"]:
            with self.subTest(name=name):
                try:
                    ActionItem.objects.get(
                        subject_identifier=self.subject_identifier,
                        action_type__name=name,
                    )
                except ObjectDoesNotExist:
                    self.fail("Action item unexpectedly does not exist.")

    def test_finds_existing_actions0(self):
        """Finds existing actions even when one is created in advance.
        """
        action_type = get_action_type(FormZeroAction)
        self.assertEqual(ActionItem.objects.all().count(), 0)
        ActionItem.objects.create(
            subject_identifier=self.subject_identifier, action_type=action_type
        )
        FormZero.objects.create(subject_identifier=self.subject_identifier)
        obj = FormZero.objects.get(subject_identifier=self.subject_identifier)
        self.assertTrue(
            ActionItem.objects.filter(action_identifier=obj.action_identifier)
        )
        self.assertEqual(ActionItem.objects.all().count(), 1)
        obj.save()
        self.assertEqual(ActionItem.objects.all().count(), 1)

    def test_finds_existing_actions1(self):
        """Finds existing actions even when many are created in advance.
        """
        # create 5 action items for FormOne
        action_type = get_action_type(FormOneAction)
        self.assertEqual(ActionItem.objects.all().count(), 0)
        for _ in range(0, 5):
            ActionItem.objects.create(
                subject_identifier=self.subject_identifier, action_type=action_type
            )
        self.assertEqual(
            ActionItem.objects.filter(
                subject_identifier=self.subject_identifier
            ).count(),
            5,
        )
        self.assertEqual(ActionItem.objects.filter(action_type=action_type).count(), 5)
        self.assertEqual(
            ActionItem.objects.filter(
                action_type=action_type,
                action_identifier__isnull=False,
                linked_to_reference=False,
            ).count(),
            5,
        )

        # create FormOne instances and expect them to link to
        # an exiting action item
        for i in range(0, 5):
            with self.subTest(index=i):
                obj = FormOne.objects.create(subject_identifier=self.subject_identifier)
                self.assertTrue(
                    ActionItem.objects.get(action_identifier=obj.action_identifier)
                )
                self.assertEqual(
                    ActionItem.objects.filter(action_type=action_type).count(), 5
                )
                self.assertEqual(
                    ActionItem.objects.filter(
                        action_type=action_type, action_identifier=obj.action_identifier
                    ).count(),
                    1,
                )

    def test_finds_existing_actions2(self):
        action_type = get_action_type(FormOneAction)
        self.assertEqual(ActionItem.objects.all().count(), 0)
        for _ in range(0, 5):
            ActionItem.objects.create(
                subject_identifier=self.subject_identifier, action_type=action_type
            )
        self.assertEqual(ActionItem.objects.all().count(), 5)
        for _ in range(0, 5):
            FormOne.objects.create(subject_identifier=self.subject_identifier)
        self.assertEqual(ActionItem.objects.filter(action_type=action_type).count(), 5)
        self.assertEqual(
            ActionItem.objects.filter(
                action_type=action_type, action_identifier__isnull=True
            ).count(),
            0,
        )

    def test_creates_next_actions(self):
        f1_action_type = get_action_type(FormOneAction)
        f2_action_type = get_action_type(FormTwoAction)
        f3_action_type = get_action_type(FormThreeAction)
        FormOne.objects.create(subject_identifier=self.subject_identifier)
        self.assertEqual(ActionItem.objects.all().count(), 3)
        self.assertEqual(
            ActionItem.objects.filter(
                subject_identifier=self.subject_identifier, action_type=f1_action_type
            ).count(),
            1,
        )
        self.assertEqual(
            ActionItem.objects.filter(
                subject_identifier=self.subject_identifier, action_type=f2_action_type
            ).count(),
            1,
        )
        self.assertEqual(
            ActionItem.objects.filter(
                subject_identifier=self.subject_identifier, action_type=f3_action_type
            ).count(),
            1,
        )

    def test_creates_next_actions2(self):
        form_one = FormOne.objects.create(subject_identifier=self.subject_identifier)
        FormTwo.objects.create(
            subject_identifier=self.subject_identifier, form_one=form_one
        )
        FormThree.objects.create(subject_identifier=self.subject_identifier)

    def test_action_is_closed_if_model_creates_action(self):

        # form_one next_actions = [FormTwoAction, FormThreeAction]
        form_one_obj = FormOne.objects.create(
            subject_identifier=self.subject_identifier
        )
        self.assertEqual(ActionItem.objects.all().count(), 3)

        # next_actions = ['self']
        FormTwo.objects.create(
            subject_identifier=self.subject_identifier,
            parent_action_item=form_one_obj.action_item,
            form_one=form_one_obj,
        )
        self.assertEqual(ActionItem.objects.all().count(), 4)

        # next_actions = [FormZeroAction]
        # should find the existing and NEW FormThreeAction
        # instead of creating one,.
        FormThree.objects.create(
            subject_identifier=self.subject_identifier,
            parent_action_item=form_one_obj.action_item,
        )
        self.assertEqual(ActionItem.objects.all().count(), 5)

        # 3 (1 for each model) are closed
        self.assertEqual(ActionItem.objects.filter(status=CLOSED).count(), 3)
        # next_actions are NEW
        self.assertEqual(ActionItem.objects.filter(status=NEW).count(), 2)

        f1_action_type = get_action_type(FormOneAction)
        f2_action_type = get_action_type(FormTwoAction)
        f3_action_type = get_action_type(FormThreeAction)

        obj = ActionItem.objects.get(
            subject_identifier=self.subject_identifier, action_type=f1_action_type
        )
        self.assertEqual(obj.status, CLOSED)

        obj = ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            action_type=f2_action_type,
            status=CLOSED,
        )
        self.assertEqual(obj.status, CLOSED)

        obj = ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            action_type=f3_action_type,
            status=CLOSED,
        )
        self.assertEqual(obj.status, CLOSED)

    def test_reference_url(self):
        action = FormOneAction(subject_identifier=self.subject_identifier)
        helper = ActionItemHelper(action_item=action.action_item)
        url = helper.get_url(model_cls=action.reference_model_cls())
        self.assertEqual(
            url,
            (
                f"/admin/edc_action_item/formone/add/?"
                f"action_identifier={action.action_identifier}"
            ),
        )

    def test_reference_url2(self):
        form_one = FormOne.objects.create(subject_identifier=self.subject_identifier)
        helper = ActionItemHelper(
            action_name=FormTwoAction.name, related_action_item=form_one.action_item
        )
        form_two_add_url = helper.reference_url
        self.assertEqual(
            form_two_add_url,
            f"/admin/edc_action_item/formtwo/add/?form_one={str(form_one.pk)}",
        )
        form_two = FormTwo.objects.create(
            subject_identifier=self.subject_identifier, form_one=form_one
        )
        helper = ActionItemHelper(action_item=form_two.action_item)
        form_two_change_url = helper.reference_url
        self.assertEqual(
            form_two_change_url,
            f"/admin/edc_action_item/formtwo/{str(form_two.pk)}/change/?"
            f"action_identifier={form_two.action_identifier}&form_one={str(form_one.pk)}",
        )

    def test_reference_url3(self):
        form_one = FormOne.objects.create(subject_identifier=self.subject_identifier)
        form_two_action = FormTwoAction(
            subject_identifier=self.subject_identifier,
            related_action_item=form_one.action_item,
        )
        helper = ActionItemHelper(action_item=form_two_action.action_item)
        self.assertEqual(
            helper.reference_url,
            (
                f"/admin/edc_action_item/formtwo/add/?"
                f"action_identifier={form_two_action.action_identifier}&"
                f"form_one={str(form_one.pk)}"
            ),
        )

    def test_create_singleton(self):

        action1 = SingletonAction(subject_identifier=self.subject_identifier)

        try:
            ActionItem.objects.get(subject_identifier=self.subject_identifier)
        except ObjectDoesNotExist:
            self.fail("ObjectDoesNotExist unexpectedly raised.")

        action2 = SingletonAction(subject_identifier=self.subject_identifier)

        self.assertEqual(action1.action_item, action2.action_item)

    def test_delete(self):
        """Assert action item is reset if reference object
        is deleted.
        """
        FormOneAction(subject_identifier=self.subject_identifier)
        action_item = ActionItem.objects.get(subject_identifier=self.subject_identifier)
        self.assertEqual(action_item.status, NEW)
        form_one = FormOne.objects.create(subject_identifier=self.subject_identifier)
        form_one = FormOne.objects.get(id=form_one.id)
        action_item = ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            action_identifier=form_one.action_identifier,
            action_type__name=FormOneAction.name,
        )
        self.assertEqual(action_item.status, CLOSED)
        form_one.delete()
        action_item = ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            action_identifier=form_one.action_identifier,
            action_type__name=FormOneAction.name,
        )
        self.assertEqual(action_item.status, NEW)

    def test_add_action_if_required(self):

        FormFourAction(subject_identifier=self.subject_identifier)
        form_four = FormFour.objects.create(
            subject_identifier=self.subject_identifier, happy=YES
        )

        self.assertRaises(
            ObjectDoesNotExist,
            ActionItem.objects.get,
            action_type=get_action_type(FormOneAction),
        )

        form_four.happy = NO
        form_four.save()
        try:
            ActionItem.objects.get(
                action_type=get_action_type(FormOneAction), status=NEW
            )
        except ObjectDoesNotExist:
            self.fail("action item unexpectedly does not exist")

        form_four.save()
        try:
            ActionItem.objects.get(
                action_type=get_action_type(FormOneAction), status=NEW
            )
        except ObjectDoesNotExist:
            self.fail("action item unexpectedly does not exist")

        form_one = FormOne.objects.create(subject_identifier=self.subject_identifier)

        form_four.save()
        try:
            ActionItem.objects.get(
                action_identifier=form_one.action_identifier, status=CLOSED
            )
        except ObjectDoesNotExist:
            self.fail("action item unexpectedly does not exist")
