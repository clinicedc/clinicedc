from django.test import TestCase, tag
from django.urls.base import reverse
from edc_action_item.models import ActionItem, ActionType
from edc_action_item.templatetags.action_item_extras import add_action_item_popover
from edc_action_item.view_mixins import ActionItemViewMixin
from edc_model_wrapper import ModelWrapper

from ..models import SubjectIdentifierModel


class MyModelWrapper(ModelWrapper):
    next_url_name = "subject_dashboard_url"


class TestAction(TestCase):
    def setUp(self):
        self.subject_identifier_model = ActionItem.subject_identifier_model
        ActionItem.subject_identifier_model = "edc_action_item.subjectidentifiermodel"
        self.subject_identifier = "12345"
        SubjectIdentifierModel.objects.create(
            subject_identifier=self.subject_identifier
        )
        ActionItemViewMixin.action_item_model_wrapper_cls = MyModelWrapper

    def test_view_context(self):
        view = ActionItemViewMixin()
        view.kwargs = dict(subject_identifier=self.subject_identifier)
        context = view.get_context_data()
        self.assertEqual(context.get("open_action_items"), [])

        for action_type in ActionType.objects.all():
            ActionItem.objects.create(
                subject_identifier=self.subject_identifier, action_type=action_type
            )

        view = ActionItemViewMixin()
        view.kwargs = dict(subject_identifier=self.subject_identifier)
        context = view.get_context_data()
        self.assertEqual(
            len(context.get("open_action_items")), ActionItem.objects.all().count()
        )

    def test_templatetag(self):
        context = add_action_item_popover(
            self.subject_identifier, "subject_dashboard_url"
        )
        reverse(context.get("action_item_add_url"))
