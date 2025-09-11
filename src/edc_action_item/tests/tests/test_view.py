from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.utils import get_user_for_tests
from django.test import RequestFactory, TestCase, override_settings, tag
from django.views.generic.base import ContextMixin, View

from edc_action_item.models import ActionItem, ActionType
from edc_action_item.view_mixins import ActionItemViewMixin
from edc_sites.utils import get_site_model_cls

from ..test_case_mixin import TestCaseMixin


class MyActionItemViewMixin(ActionItemViewMixin, ContextMixin, View):
    pass


utc_tz = ZoneInfo("UTC")


@tag("action_item")
@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=utc_tz))
@override_settings(SITE_ID=30)
class TestAction(TestCaseMixin, TestCase):
    def setUp(self):
        self.subject_identifier = self.fake_enroll()
        self.user = get_user_for_tests()
        self.site = get_site_model_cls().objects.get_current()

    def test_view_context(self):
        req = RequestFactory().get("/")
        req.user = self.user
        req.site = self.site
        view = MyActionItemViewMixin()
        view.request = req
        view.kwargs = dict(subject_identifier=self.subject_identifier)
        context = view.get_context_data()
        self.assertEqual(context.get("open_action_items").count(), 0)

        for action_type in ActionType.objects.all():
            ActionItem.objects.create(
                subject_identifier=self.subject_identifier, action_type=action_type
            )

        view = MyActionItemViewMixin()
        view.request = req
        view.kwargs = dict(subject_identifier=self.subject_identifier)
        context = view.get_context_data()
        self.assertEqual(
            len(context.get("open_action_items")), ActionItem.objects.all().count()
        )
