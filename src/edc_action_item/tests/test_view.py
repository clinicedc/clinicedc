from django.test import TestCase, tag
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import CLOSED, OPEN
from edc_model_wrapper import ModelWrapper

from ..models import ActionItem, ActionType
from ..site_action_items import site_action_items
from ..templatetags.action_item_extras import action_item_with_popover
from .action_items import FormOneAction, FormTwoAction, FormThreeAction, FormZeroAction
from .models import FormZero, FormOne, FormTwo, FormThree, SubjectIdentifierModel
from edc_action_item.view_mixins.action_item_view_mixin import ActionItemViewMixin
from pprint import pprint
from edc_action_item.templatetags.action_item_extras import action_item_control
from django.urls.base import reverse


class MyModelWrapper(ModelWrapper):
    next_url_name = 'dashboard_url'


class TestAction(TestCase):

    def setUp(self):
        self.subject_identifier_model = ActionItem.subject_identifier_model
        ActionItem.subject_identifier_model = 'edc_action_item.subjectidentifiermodel'
        self.subject_identifier = '12345'
        SubjectIdentifierModel.objects.create(
            subject_identifier=self.subject_identifier)
        ActionItemViewMixin.action_item_model_wrapper_cls = MyModelWrapper

    def test_view_populates_action_type(self):
        self.assertEqual(ActionType.objects.all().count(), 0)
        ActionItemViewMixin()
        self.assertGreater(ActionType.objects.all().count(), 0)
        ActionItemViewMixin()
        self.assertGreater(ActionType.objects.all().count(), 0)

    def test_view_context(self):
        view = ActionItemViewMixin()
        view.kwargs = dict(subject_identifier=self.subject_identifier)
        context = view.get_context_data()
        self.assertEqual(context.get('open_action_items'), [])

        for action_type in ActionType.objects.all():
            ActionItem.objects.create(
                subject_identifier=self.subject_identifier,
                action_type=action_type)

        view = ActionItemViewMixin()
        view.kwargs = dict(subject_identifier=self.subject_identifier)
        context = view.get_context_data()
        self.assertEqual(len(context.get('open_action_items')),
                         ActionItem.objects.all().count())

    def test_templatetag(self):
        context = action_item_control(
            self.subject_identifier, 'subject_dashboard_url')
        reverse(context.get('action_item_add_url'))
