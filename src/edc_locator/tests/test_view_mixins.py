from django.test import TestCase

from ..view_mixins import SubjectLocatorViewMixin, SubjectLocatorViewMixinError
from django.http.request import HttpRequest
from django.contrib.messages.storage.fallback import FallbackStorage
from pprint import pprint


class DummyModelWrapper:
    def __init__(self, **kwargs):
        pass


class TestViewMixins(TestCase):

    def test_subject_locator_raises_on_bad_model(self):

        class MySubjectLocatorViewMixin(SubjectLocatorViewMixin):
            subject_locator_model_wrapper_cls = DummyModelWrapper
            subject_locator_model = 'blah.blahblah'
        mixin = MySubjectLocatorViewMixin()
        self.assertRaises(
            SubjectLocatorViewMixinError,
            mixin.get_context_data)

    def test_subject_locator_raisesmissing_wrapper_cls(self):

        class MySubjectLocatorViewMixin(SubjectLocatorViewMixin):
            subject_locator_model = 'edc_locator.subjectlocator'
        self.assertRaises(
            SubjectLocatorViewMixinError,
            MySubjectLocatorViewMixin)

    def test_mixin_messages(self):

        class MySubjectLocatorViewMixin(SubjectLocatorViewMixin):
            subject_locator_model_wrapper_cls = DummyModelWrapper
            subject_locator_model = 'edc_locator.subjectlocator'

        mixin = MySubjectLocatorViewMixin()
        mixin.kwargs = {'subject_identifier': '12345'}
        mixin.request = HttpRequest()
        setattr(mixin.request, 'session', 'session')
        messages = FallbackStorage(mixin.request)
        setattr(mixin.request, '_messages', messages)
        self.assertGreater(len(mixin.request._messages._queued_messages), 0)

    def test_subject_locator_ok(self):

        class MySubjectLocatorViewMixin(SubjectLocatorViewMixin):
            subject_locator_model_wrapper_cls = DummyModelWrapper
            subject_locator_model = 'edc_locator.subjectlocator'

        mixin = MySubjectLocatorViewMixin()
        mixin.request = HttpRequest()
        setattr(mixin.request, 'session', 'session')
        messages = FallbackStorage(mixin.request)
        setattr(mixin.request, '_messages', messages)
        # add this manually
        mixin.kwargs = {'subject_identifier': '12345'}
        try:
            mixin.get_context_data()
        except SubjectLocatorViewMixinError as e:
            self.fail(e)
