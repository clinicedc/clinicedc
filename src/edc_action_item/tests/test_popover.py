from django.test import TestCase, tag
from django.conf import settings
from edc_constants.constants import CLOSED, OPEN, NEW
from edc_model_wrapper import ModelWrapper

from ..models import ActionItem, ActionType
from ..site_action_items import site_action_items
from ..templatetags.action_item_extras import action_item_with_popover
from .action_items import FormOneAction, FormTwoAction, FormThreeAction
from .action_items import register_actions
from .models import FormOne, FormTwo, SubjectIdentifierModel, Initial, Followup


class TestPopover(TestCase):

    def setUp(self):
        register_actions()
        self.subject_identifier_model = ActionItem.subject_identifier_model
        ActionItem.subject_identifier_model = 'edc_action_item.subjectidentifiermodel'
        self.subject_identifier = '12345'
        SubjectIdentifierModel.objects.create(
            subject_identifier=self.subject_identifier)
        self.assertEqual(0, ActionType.objects.all().count())
        self.assertIn(FormOneAction.name, site_action_items.registry)
        self.assertIn(FormTwoAction.name, site_action_items.registry)
        self.assertIn(FormThreeAction.name, site_action_items.registry)

    def tearDown(self):
        ActionItem.subject_identifier_model = self.subject_identifier_model

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
        self.assertIsNone(context.get('parent_reference_identifier'))
        self.assertIsNone(context.get('parent_action_item'))

        form_two = FormTwo.objects.create(
            subject_identifier=self.subject_identifier,
            form_one=form_one)
        obj = ActionItem.objects.get(
            action_identifier=form_two.action_identifier)
        wrapper = ActionItemModelWrapper(model_obj=obj)
        context = action_item_with_popover(wrapper, 0)
        self.assertEqual(context.get('parent_reference_identifier'),
                         form_one.action_identifier)
        self.assertEqual(context.get('parent_action_item'),
                         form_one.action_item)

        context = action_item_with_popover(wrapper, 0)
        self.assertEqual(context.get('parent_reference_identifier'),
                         form_one.action_identifier)
        self.assertEqual(context.get('parent_action_item'),
                         form_one.action_item)

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
        reference_url = context.get('reference_url')
        self.assertIn(f'{str(form_one.pk)}', reference_url)
        self.assertTrue(
            reference_url.startswith(
                f'/admin/edc_action_item/formone/{str(form_one.pk)}/change/'),
            msg=reference_url)

    def test_popover_templatetag2(self):

        class ActionItemModelWrapper(ModelWrapper):

            model = 'edc_action_item.actionitem'
            next_url_attrs = ['subject_identifier']
            next_url_name = settings.DASHBOARD_URL_NAMES.get(
                'subject_dashboard_url')

            @property
            def subject_identifier(self):
                return self.object.subject_identifier

        Initial.objects.create(
            subject_identifier=self.subject_identifier)
        Initial.objects.create(
            subject_identifier=self.subject_identifier)
        initial_obj = Initial.objects.create(
            subject_identifier=self.subject_identifier)
        initial_action_item_obj = ActionItem.objects.get(
            action_identifier=initial_obj.action_identifier)

        # assert initial action is correct
        self.assertEqual(initial_action_item_obj.subject_identifier,
                         initial_obj.subject_identifier)
        self.assertEqual(initial_action_item_obj.action_identifier,
                         initial_obj.action_identifier)
        self.assertIsNone(initial_action_item_obj.parent_reference_identifier)
        self.assertIsNone(initial_action_item_obj.parent_action_item_id)
        self.assertEqual(initial_action_item_obj.action_identifier,
                         initial_obj.action_identifier)

        # assert initial action is closed
        self.assertTrue(initial_action_item_obj.status == CLOSED)

        # assert followup action was created
        followup_action_obj = ActionItem.objects.get(
            parent_action_item_id=initial_action_item_obj.pk)

        # assert followup action is new
        self.assertTrue(followup_action_obj.status == NEW)

        # assert followup "add" url points to initial model obj fk
        wrapper = ActionItemModelWrapper(model_obj=followup_action_obj)
        action_item_with_popover(wrapper, 0)
        context = action_item_with_popover(wrapper, 0)
        reference_url = context.get('reference_url')
        self.assertIn('add', reference_url)
        self.assertIn(f'initial={str(initial_obj.pk)}', reference_url)

        # add a followup model instance
        followup_obj = Followup.objects.create(
            subject_identifier=initial_obj.subject_identifier,
            parent_reference_identifier=initial_obj.action_identifier,
            initial=initial_obj)

        # assert followup_obj has action identifier
        self.assertEqual(followup_obj.action_identifier,
                         followup_action_obj.action_identifier)
        self.assertIsNotNone(followup_obj.action_identifier)

        # requery followup action
        followup_action_obj = ActionItem.objects.get(pk=followup_action_obj.pk)

        # assert followup 'change' url points to initial model obj
        followup_action_obj.status = OPEN
        followup_action_obj.save()
        wrapper = ActionItemModelWrapper(model_obj=followup_action_obj)
        action_item_with_popover(wrapper, 0)
        context = action_item_with_popover(wrapper, 0)
        reference_url = context.get('reference_url')
        # assert followup change url points to initial model obj
        self.assertIn('change', reference_url)
        self.assertIn(f'initial={str(initial_obj.pk)}', reference_url)

    def test_popover_templatetag3(self):

        class ActionItemModelWrapper(ModelWrapper):

            model = 'edc_action_item.actionitem'
            next_url_attrs = ['subject_identifier']
            next_url_name = settings.DASHBOARD_URL_NAMES.get(
                'subject_dashboard_url')

            @property
            def subject_identifier(self):
                return self.object.subject_identifier

        Initial.objects.create(
            subject_identifier=self.subject_identifier)

        initial_obj1 = Initial.objects.create(
            subject_identifier=self.subject_identifier)

        initial_obj2 = Initial.objects.create(
            subject_identifier=self.subject_identifier)

        followup_action_obj = ActionItem.objects.get(
            parent_reference_identifier=initial_obj1.action_identifier)
        wrapper = ActionItemModelWrapper(model_obj=followup_action_obj)
        action_item_with_popover(wrapper, 0)
        context = action_item_with_popover(wrapper, 0)
        reference_url = context.get('reference_url')
        self.assertIn(f'initial={str(initial_obj1.pk)}', reference_url)

        followup_action_obj = ActionItem.objects.get(
            parent_reference_identifier=initial_obj2.action_identifier)
        wrapper = ActionItemModelWrapper(model_obj=followup_action_obj)
        action_item_with_popover(wrapper, 0)
        context = action_item_with_popover(wrapper, 0)
        reference_url = context.get('reference_url')
        self.assertIn(f'initial={str(initial_obj2.pk)}', reference_url)

    def test_popover_templatetag4(self):

        class ActionItemModelWrapper(ModelWrapper):

            model = 'edc_action_item.actionitem'
            next_url_attrs = ['subject_identifier']
            next_url_name = settings.DASHBOARD_URL_NAMES.get(
                'subject_dashboard_url')

            @property
            def subject_identifier(self):
                return self.object.subject_identifier

        Initial.objects.create(
            subject_identifier=self.subject_identifier)

        initial_obj1 = Initial.objects.create(
            subject_identifier=self.subject_identifier)

        Initial.objects.create(
            subject_identifier=self.subject_identifier)

        followup_obj1 = Followup.objects.create(
            subject_identifier=initial_obj1.subject_identifier,
            parent_reference_identifier=initial_obj1.action_identifier,
            initial=initial_obj1)

        ActionItem.objects.get(
            subject_identifier=initial_obj1.subject_identifier,
            related_reference_identifier=initial_obj1.action_identifier,
            parent_reference_identifier=initial_obj1.action_identifier)

        followup_action_obj2 = ActionItem.objects.get(
            subject_identifier=initial_obj1.subject_identifier,
            related_reference_identifier=initial_obj1.action_identifier,
            parent_reference_identifier=followup_obj1.action_identifier)

        wrapper = ActionItemModelWrapper(model_obj=followup_action_obj2)
        action_item_with_popover(wrapper, 0)
        context = action_item_with_popover(wrapper, 0)
        reference_url = context.get('reference_url')
        self.assertIn(f'initial={str(initial_obj1.pk)}', reference_url)
