from django.test import TestCase, tag
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import CLOSED, OPEN
from edc_model_wrapper import ModelWrapper

from ..action import create_action_item, delete_action_item
from ..action import ActionItemDeleteError, SingletonActionItemError
from ..models import ActionItem, ActionType
from ..site_action_items import site_action_items
from ..templatetags.action_item_extras import action_item_with_popover
from .action_items import FormOneAction, FormTwoAction, FormThreeAction, FormZeroAction
from .action_items import SingletonAction
from .models import FormZero, FormOne, FormTwo, FormThree, SubjectIdentifierModel
from pprint import pprint


class TestAction(TestCase):

    def setUp(self):
        self.subject_identifier_model = ActionItem.subject_identifier_model
        ActionItem.subject_identifier_model = 'edc_action_item.subjectidentifiermodel'
        self.subject_identifier = '12345'
        SubjectIdentifierModel.objects.create(
            subject_identifier=self.subject_identifier)
        self.assertEqual(0, ActionType.objects.all().count())
        self.assertIn(FormOneAction.name, site_action_items.registry)
        self.assertIn(FormTwoAction.name, site_action_items.registry)
        self.assertIn(FormThreeAction.name, site_action_items.registry)

    def test_str(self):
        action = FormZero.action_cls(
            subject_identifier=self.subject_identifier)
        self.assertTrue(str(action))

    def test_populate_action_types(self):
        site_action_items.populate_action_types()
        self.assertGreater(len(site_action_items.registry), 0)
        self.assertEqual(ActionType.objects.all().count(),
                         len(site_action_items.registry))

    def test_populate_action_types2(self):
        site_action_items.populate_action_types()
        self.assertGreater(len(site_action_items.registry), 0)
        self.assertEqual(ActionType.objects.all().count(),
                         len(site_action_items.registry))

    def test_creates_own_action0(self):
        obj = FormZero.objects.create(
            subject_identifier=self.subject_identifier)
        try:
            obj = ActionItem.objects.get(
                action_identifier=obj.action_identifier)
        except ObjectDoesNotExist:
            self.fail('Action item unexpectedly does not exist')
        for name in ['submit-form-zero']:
            with self.subTest(name=name):
                try:
                    ActionItem.objects.get(
                        subject_identifier=self.subject_identifier,
                        action_type__name=name)
                except ObjectDoesNotExist:
                    self.fail('Action item unexpectedly does not exist.')
        self.assertEqual(ActionItem.objects.filter(
            subject_identifier=self.subject_identifier).count(), 1)

    def test_check_attrs_for_own_action0(self):
        obj = FormZero.objects.create(
            subject_identifier=self.subject_identifier)
        action_type = FormZero.action_cls.action_type()
        action_item = ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            action_type__name='submit-form-zero')
        self.assertEqual(action_item.subject_identifier,
                         obj.subject_identifier)
        self.assertEqual(action_item.action_identifier, obj.action_identifier)
        self.assertEqual(action_item.reference_identifier,
                         obj.tracking_identifier)
        self.assertEqual(action_item.reference_model,
                         obj._meta.label_lower)
        self.assertIsNone(action_item.parent_reference_identifier)
        self.assertIsNone(action_item.parent_model)
        self.assertIsNone(action_item.parent_action_item)
        self.assertEqual(action_item.action_type, action_type)

    def test_check_attrs_for_form_one_next_action(self):
        obj = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        action_type_two = FormTwo.action_cls.action_type()
        action_item_one = ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            action_type__name='submit-form-one')
        action_item_two = ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            action_type__name='submit-form-two')
        self.assertEqual(action_item_two.subject_identifier,
                         obj.subject_identifier)
        self.assertNotEqual(action_item_two.action_identifier,
                            obj.action_identifier)
        self.assertNotEqual(action_item_two.reference_identifier,
                            obj.tracking_identifier)
        self.assertEqual(action_item_two.reference_model,
                         FormTwo._meta.label_lower)
        self.assertEqual(action_item_two.parent_reference_identifier,
                         obj.tracking_identifier)
        self.assertEqual(action_item_two.parent_model,
                         FormOne._meta.label_lower)
        self.assertEqual(action_item_two.parent_action_item, action_item_one)
        self.assertEqual(action_item_two.action_type, action_type_two)

    def test_does_not_duplicate_own_action_on_save(self):
        obj = FormZero.objects.create(
            subject_identifier=self.subject_identifier)
        obj.save()
        for name in ['submit-form-zero']:
            with self.subTest(name=name):
                try:
                    ActionItem.objects.get(
                        subject_identifier=self.subject_identifier,
                        action_type__name=name)
                except ObjectDoesNotExist:
                    self.fail('Action item unexpectedly does not exist.')
        self.assertEqual(ActionItem.objects.filter(
            subject_identifier=self.subject_identifier).count(), 1)

    def test_creates_own_action1(self):
        obj = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        try:
            obj = ActionItem.objects.get(
                action_identifier=obj.action_identifier)
        except ObjectDoesNotExist:
            self.fail('Action item unexpectedly does not exist')
        for name in ['submit-form-one', 'submit-form-two', 'submit-form-three']:
            with self.subTest(name=name):
                try:
                    ActionItem.objects.get(
                        subject_identifier=self.subject_identifier,
                        action_type__name=name)
                except ObjectDoesNotExist:
                    self.fail('Action item unexpectedly does not exist.')
        self.assertEqual(ActionItem.objects.filter(
            subject_identifier=self.subject_identifier).count(), 3)

    def test_does_not_duplicate_own_actions_on_save(self):
        obj = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        obj.save()
        for name in ['submit-form-one', 'submit-form-two', 'submit-form-three']:
            with self.subTest(name=name):
                try:
                    ActionItem.objects.get(
                        subject_identifier=self.subject_identifier,
                        action_type__name=name)
                except ObjectDoesNotExist:
                    self.fail('Action item unexpectedly does not exist.')
        self.assertEqual(ActionItem.objects.filter(
            subject_identifier=self.subject_identifier).count(), 3)

    def test_finds_existing_actions0(self):
        """Finds existing actions even when one is created in advance.
        """
        action_type = FormZeroAction.action_type()
        self.assertEqual(ActionItem.objects.all().count(), 0)
        ActionItem.objects.create(
            subject_identifier=self.subject_identifier,
            action_type=action_type)
        FormZero.objects.create(
            subject_identifier=self.subject_identifier)
        obj = FormZero.objects.get(
            subject_identifier=self.subject_identifier)
        self.assertTrue(
            ActionItem.objects.filter(action_identifier=obj.action_identifier))
        self.assertEqual(ActionItem.objects.all().count(), 1)
        obj.save()
        self.assertEqual(ActionItem.objects.all().count(), 1)

    def test_finds_existing_actions1(self):
        """Finds existing actions even when many are created in advance.
        """
        # create 5 action items for FormOne
        action_type = FormOneAction.action_type()
        self.assertEqual(ActionItem.objects.all().count(), 0)
        for _ in range(0, 5):
            ActionItem.objects.create(
                subject_identifier=self.subject_identifier,
                action_type=action_type)
        self.assertEqual(ActionItem.objects.filter(
            subject_identifier=self.subject_identifier).count(), 5)
        self.assertEqual(ActionItem.objects.filter(
            action_type=action_type).count(), 5)
        self.assertEqual(ActionItem.objects.filter(
            action_type=action_type,
            reference_identifier__isnull=True).count(), 5)

        # create FormOne instances and expect them to link to
        # an exiting action item
        for i in range(0, 5):
            with self.subTest(index=i):
                obj = FormOne.objects.create(
                    subject_identifier=self.subject_identifier)
                self.assertIsNotNone(obj.tracking_identifier)
                self.assertTrue(
                    ActionItem.objects.get(
                        action_identifier=obj.action_identifier))
                self.assertEqual(ActionItem.objects.filter(
                    action_type=action_type).count(), 5)
                self.assertEqual(ActionItem.objects.filter(
                    action_type=action_type,
                    reference_identifier=obj.tracking_identifier).count(), 1)

    def test_finds_existing_actions2(self):
        action_type = FormOneAction.action_type()
        self.assertEqual(ActionItem.objects.all().count(), 0)
        for _ in range(0, 5):
            ActionItem.objects.create(
                subject_identifier=self.subject_identifier,
                action_type=action_type)
        self.assertEqual(ActionItem.objects.all().count(), 5)
        for _ in range(0, 5):
            FormOne.objects.create(
                subject_identifier=self.subject_identifier)
        self.assertEqual(ActionItem.objects.filter(
            action_type=action_type).count(), 5)
        self.assertEqual(ActionItem.objects.filter(
            action_type=action_type,
            reference_identifier__isnull=True).count(), 0)

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

    def test_reference_model_delete_resets_action_item(self):
        obj = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        action_item = ActionItem.objects.get(
            action_identifier=obj.action_identifier)
        self.assertEqual(action_item.status, CLOSED)
        obj.delete()
        action_item = ActionItem.objects.get(
            action_identifier=obj.action_identifier)
        self.assertEqual(action_item.status, OPEN)
        self.assertIsNone(action_item.reference_identifier)

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
            f'/admin/edc_action_item/formtwo/add/?form_one={str(form_one.pk)}')

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
            (f'/admin/edc_action_item/formtwo/add/?subject_identifier='
             f'{self.subject_identifier}&form_one={str(form_one.pk)}'))

    def test_reference_model_url5(self):
        form_one = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        form_two = FormTwo.objects.create(
            subject_identifier=self.subject_identifier,
            form_one=form_one)
        action_item = ActionItem.objects.get(
            action_identifier=form_two.action_identifier)
        url = FormTwoAction(model_obj=form_two).reference_model_url(
            model_obj=form_two,
            action_item=action_item,
            subject_identifier=self.subject_identifier)
        self.assertEqual(
            url,
            (f'/admin/edc_action_item/formtwo/{str(form_two.pk)}/change/?'
             f'subject_identifier={self.subject_identifier}&form_one={str(form_one.pk)}'))

    def test_popover_templatetag(self):

        class ActionItemModelWrapper(ModelWrapper):

            model = 'edc_action_item.actionitem'
            next_url_attrs = ['subject_identifier']
            next_url_name = settings.DASHBOARD_URL_NAMES.get(
                'subject_dashboard_url')

            @property
            def subject_identifier(self):
                return self.object.subject_identifier

        form_one = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        obj = ActionItem.objects.get(
            action_identifier=form_one.action_identifier)
        wrapper = ActionItemModelWrapper(model_obj=obj)
        action_item_with_popover(wrapper, 0)
        context = action_item_with_popover(wrapper, 0)
        self.assertIsNone(context.get('parent_action_identifier'))
        self.assertIsNone(context.get('parent_action_item'))

        form_two = FormTwo.objects.create(
            subject_identifier=self.subject_identifier,
            form_one=form_one)
        obj = ActionItem.objects.get(
            action_identifier=form_two.action_identifier)
        wrapper = ActionItemModelWrapper(model_obj=obj)
        context = action_item_with_popover(wrapper, 0)
        self.assertEqual(context.get('parent_action_identifier'),
                         form_one.action_identifier)
        self.assertEqual(context.get('parent_action_item'),
                         form_one.action_item)

        context = action_item_with_popover(wrapper, 0)
        self.assertEqual(context.get('parent_action_identifier'),
                         form_one.action_identifier)
        self.assertEqual(context.get('parent_action_item'),
                         form_one.action_item)

    @tag('1')
    def test_popover_templatetag_action_url_if_reference_model_exists(self):
        """Asserts returns a change url if reference model
        exists.
        """
        class ActionItemModelWrapper(ModelWrapper):

            model = 'edc_action_item.actionitem'
            next_url_attrs = ['subject_identifier']
            next_url_name = settings.DASHBOARD_URL_NAMES.get(
                'subject_dashboard_url')

            @property
            def subject_identifier(self):
                return self.object.subject_identifier

        form_one = FormOne.objects.create(
            subject_identifier=self.subject_identifier)
        obj = ActionItem.objects.get(
            action_identifier=form_one.action_identifier)
        self.assertTrue(obj.status == CLOSED)
        obj.status = OPEN
        obj.save()
        wrapper = ActionItemModelWrapper(model_obj=obj)
        action_item_with_popover(wrapper, 0)
        context = action_item_with_popover(wrapper, 0)
        url = context.get('model_url')
        self.assertTrue(
            url.startswith(
                f'/admin/edc_action_item/formone/{str(form_one.pk)}/change/'), msg=url)

    def test_create(self):
        create_action_item(
            action_cls=SingletonAction,
            subject_identifier=self.subject_identifier)
        try:
            ActionItem.objects.get(subject_identifier=self.subject_identifier)
        except ObjectDoesNotExist:
            self.fail('ObjectDoesNotExist unexpectedly raised.')
        self.assertRaises(
            SingletonActionItemError,
            create_action_item,
            action_cls=SingletonAction,
            subject_identifier=self.subject_identifier)

    def test_delete(self):
        create_action_item(
            action_cls=SingletonAction,
            subject_identifier=self.subject_identifier)
        delete_action_item(
            action_cls=SingletonAction,
            subject_identifier=self.subject_identifier)
        self.assertRaises(
            ObjectDoesNotExist,
            ActionItem.objects.get,
            subject_identifier=self.subject_identifier)

    def test_cannot_delete_if_not_new(self):
        action_item = create_action_item(
            action_cls=SingletonAction,
            subject_identifier=self.subject_identifier)
        action_item.status = CLOSED
        action_item.save()
        self.assertRaises(
            ActionItemDeleteError,
            delete_action_item,
            action_cls=SingletonAction,
            subject_identifier=self.subject_identifier)
        action_item.status = OPEN
        action_item.save()
        self.assertRaises(
            ActionItemDeleteError,
            delete_action_item,
            action_cls=SingletonAction,
            subject_identifier=self.subject_identifier)
