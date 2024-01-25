from unittest.case import skip

from django.test import TestCase, tag
from django.views.generic.base import ContextMixin
from edc_action_item import site_action_items
from edc_action_item.models import ActionItem
from edc_registration.models import RegisteredSubject
from edc_sites.view_mixins import SiteViewMixin
from edc_subject_dashboard.view_mixins import RegisteredSubjectViewMixin
from edc_test_utils.get_httprequest_for_tests import get_request_object_for_tests
from edc_test_utils.get_user_for_tests import get_user_for_tests

from edc_locator.action_items import SUBJECT_LOCATOR_ACTION
from edc_locator.exceptions import SubjectLocatorViewMixinError
from edc_locator.view_mixins import SubjectLocatorViewMixin


class TestViewMixins(TestCase):
    def setUp(self):
        self.user = get_user_for_tests()
        self.subject_identifier = "12345"
        RegisteredSubject.objects.create(subject_identifier=self.subject_identifier)

    def test_subject_locator_raises_on_bad_model(self):
        class MySubjectLocatorViewMixin(
            SiteViewMixin, SubjectLocatorViewMixin, RegisteredSubjectViewMixin, ContextMixin
        ):
            subject_locator_model = "blah.blahblah"

        mixin = MySubjectLocatorViewMixin()
        mixin.kwargs = {"subject_identifier": self.subject_identifier}
        mixin.request = get_request_object_for_tests(self.user)
        self.assertRaises(LookupError, mixin.get_context_data)

    @skip("problems emulating message framework")
    def test_mixin_messages(self):
        class MySubjectLocatorViewMixin(
            SiteViewMixin, SubjectLocatorViewMixin, RegisteredSubjectViewMixin, ContextMixin
        ):
            subject_locator_model = "edc_locator.subjectlocator"

        mixin = MySubjectLocatorViewMixin()
        mixin.kwargs = {"subject_identifier": self.subject_identifier}
        mixin.request = get_request_object_for_tests(self.user)
        self.assertGreater(len(mixin.request._messages._queued_messages), 0)

    @tag("1")
    def test_subject_locator_view_ok(self):
        class MySubjectLocatorViewMixin(
            SiteViewMixin, SubjectLocatorViewMixin, RegisteredSubjectViewMixin, ContextMixin
        ):
            subject_locator_model = "edc_locator.subjectlocator"

        mixin = MySubjectLocatorViewMixin()
        mixin.request = get_request_object_for_tests(self.user)
        mixin.kwargs = {"subject_identifier": self.subject_identifier}
        try:
            mixin.get_context_data()
        except SubjectLocatorViewMixinError as e:
            self.fail(e)

    def test_subject_locator_self_corrects_if_multiple_actionitems(self):
        class MySubjectLocatorViewMixin(
            SiteViewMixin, SubjectLocatorViewMixin, RegisteredSubjectViewMixin, ContextMixin
        ):
            subject_locator_model = "edc_locator.subjectlocator"

        mixin = MySubjectLocatorViewMixin()
        mixin.request = get_request_object_for_tests(self.user)
        mixin.kwargs = {"subject_identifier": self.subject_identifier}
        try:
            mixin.get_context_data()
        except SubjectLocatorViewMixinError as e:
            self.fail(e)
        action_cls = site_action_items.get(SUBJECT_LOCATOR_ACTION)
        action_item_model_cls = action_cls.action_item_model_cls()
        action_cls(subject_identifier=self.subject_identifier)
        action_item = ActionItem.objects.get(subject_identifier=self.subject_identifier)
        self.assertEqual(action_item_model_cls.objects.all().count(), 1)
        action_item.subject_identifier = f"{self.subject_identifier}-bad"
        action_item.save()
        self.assertEqual(action_item_model_cls.objects.all().count(), 1)
        action_cls = site_action_items.get(SUBJECT_LOCATOR_ACTION)
        action_cls(subject_identifier=self.subject_identifier)
        action_item.subject_identifier = self.subject_identifier
        action_item.save()
        self.assertEqual(action_item_model_cls.objects.all().count(), 2)
        try:
            mixin.get_context_data()
        except SubjectLocatorViewMixinError as e:
            self.fail(e)
        self.assertEqual(action_item_model_cls.objects.all().count(), 1)
