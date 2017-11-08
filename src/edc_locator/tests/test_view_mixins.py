from django.test import TestCase
from edc_subject_dashboard.view_mixins import SubjectIdentifierViewMixin

from ..view_mixins import SubjectLocatorViewMixin, SubjectLocatorViewMixinError


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

    def test_subject_locator_must_be_declared_with_identifier_mixin(self):

        class MySubjectLocatorViewMixin(SubjectLocatorViewMixin):
            subject_locator_model_wrapper_cls = DummyModelWrapper
            subject_locator_model = 'edc_locator.subjectlocator'

        mixin = MySubjectLocatorViewMixin()
        mixin.kwargs = {'subject_identifier': '12345'}
        self.assertRaises(
            SubjectLocatorViewMixinError,
            mixin.get_context_data)

    def test_subject_locator_ok(self):

        class MySubjectLocatorViewMixin(SubjectIdentifierViewMixin, SubjectLocatorViewMixin):
            subject_locator_model_wrapper_cls = DummyModelWrapper
            subject_locator_model = 'edc_locator.subjectlocator'

        mixin = MySubjectLocatorViewMixin()
        # add this manually
        mixin.kwargs = {'subject_identifier': '12345'}
        try:
            mixin.get_context_data()
        except SubjectLocatorViewMixinError as e:
            self.fail(e)
