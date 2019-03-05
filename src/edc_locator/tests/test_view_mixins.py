from django.contrib.messages.storage.fallback import FallbackStorage
from django.http.request import HttpRequest
from django.test import TestCase
from edc_registration.models import RegisteredSubject
from unittest.case import skip

from ..view_mixins import SubjectLocatorViewMixin, SubjectLocatorViewMixinError


class DummyModelWrapper:
    def __init__(self, **kwargs):
        pass


class TestViewMixins(TestCase):
    def setUp(self):
        self.subject_identifier = "12345"
        RegisteredSubject.objects.create(subject_identifier=self.subject_identifier)

    def test_subject_locator_raises_on_bad_model(self):
        class MySubjectLocatorViewMixin(SubjectLocatorViewMixin):
            subject_locator_model_wrapper_cls = DummyModelWrapper
            subject_locator_model = "blah.blahblah"

        mixin = MySubjectLocatorViewMixin()
        self.assertRaises(SubjectLocatorViewMixinError, mixin.get_context_data)

    def test_subject_locator_raisesmissing_wrapper_cls(self):
        class MySubjectLocatorViewMixin(SubjectLocatorViewMixin):
            subject_locator_model = "edc_locator.subjectlocator"

        self.assertRaises(SubjectLocatorViewMixinError, MySubjectLocatorViewMixin)

    @skip("problems emulating message framework")
    def test_mixin_messages(self):
        class MySubjectLocatorViewMixin(SubjectLocatorViewMixin):
            subject_locator_model_wrapper_cls = DummyModelWrapper
            subject_locator_model = "edc_locator.subjectlocator"

        mixin = MySubjectLocatorViewMixin()
        mixin.kwargs = {"subject_identifier": self.subject_identifier}
        mixin.request = HttpRequest()
        setattr(mixin.request, "session", "session")
        messages = FallbackStorage(mixin.request)
        setattr(mixin.request, "_messages", messages)
        self.assertGreater(len(mixin.request._messages._queued_messages), 0)

    def test_subject_locator_ok(self):
        class MySubjectLocatorViewMixin(SubjectLocatorViewMixin):
            subject_locator_model_wrapper_cls = DummyModelWrapper
            subject_locator_model = "edc_locator.subjectlocator"

        mixin = MySubjectLocatorViewMixin()
        mixin.request = HttpRequest()
        setattr(mixin.request, "session", "session")
        messages = FallbackStorage(mixin.request)
        setattr(mixin.request, "_messages", messages)
        # add this manually
        mixin.kwargs = {"subject_identifier": self.subject_identifier}
        try:
            mixin.get_context_data()
        except SubjectLocatorViewMixinError as e:
            self.fail(e)
