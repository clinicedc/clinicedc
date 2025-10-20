from unittest.case import skip

from clinicedc_tests.action_items import register_actions
from clinicedc_tests.utils import get_request_object_for_tests, get_user_for_tests
from django.test import TestCase, override_settings, tag
from django.views.generic.base import ContextMixin

from edc_action_item.models import ActionItem
from edc_action_item.site_action_items import site_action_items
from edc_locator.action_items import SUBJECT_LOCATOR_ACTION
from edc_locator.exceptions import SubjectLocatorViewMixinError
from edc_locator.view_mixins import SubjectLocatorViewMixin
from edc_registration.models import RegisteredSubject
from edc_sites.view_mixins import SiteViewMixin
from edc_subject_dashboard.view_mixins import RegisteredSubjectViewMixin


@tag("locator")
@override_settings(SITE_ID=10)
class TestViewMixins(TestCase):
    def setUp(self):
        self.user = get_user_for_tests()
        self.subject_identifier = "12345"
        RegisteredSubject.objects.create(subject_identifier=self.subject_identifier)
        register_actions()

    def test_subject_locator_raises_on_bad_model(self):
        class MySubjectLocatorViewMixin(
            SiteViewMixin,
            SubjectLocatorViewMixin,
            RegisteredSubjectViewMixin,
            ContextMixin,
        ):
            subject_locator_model = "blah.blahblah"

        mixin = MySubjectLocatorViewMixin()
        mixin.kwargs = {"subject_identifier": self.subject_identifier}
        mixin.request = get_request_object_for_tests(self.user)
        self.assertRaises(LookupError, mixin.get_context_data)

    @skip("problems emulating message framework")
    def test_mixin_messages(self):
        class MySubjectLocatorViewMixin(
            SiteViewMixin,
            SubjectLocatorViewMixin,
            RegisteredSubjectViewMixin,
            ContextMixin,
        ):
            subject_locator_model = "edc_locator.subjectlocator"

        mixin = MySubjectLocatorViewMixin()
        mixin.kwargs = {"subject_identifier": self.subject_identifier}
        mixin.request = get_request_object_for_tests(self.user)
        self.assertGreater(len(mixin.request._messages._queued_messages), 0)

    def test_subject_locator_view_ok(self):
        class MySubjectLocatorViewMixin(
            SiteViewMixin,
            SubjectLocatorViewMixin,
            RegisteredSubjectViewMixin,
            ContextMixin,
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
            SiteViewMixin,
            SubjectLocatorViewMixin,
            RegisteredSubjectViewMixin,
            ContextMixin,
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
