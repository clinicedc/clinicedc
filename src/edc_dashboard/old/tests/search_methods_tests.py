from django.core.paginator import Page
from django.db.models.query import QuerySet
from django.test import TestCase

from edc.dashboard.section.classes import BaseSectionView, site_sections
from edc_testing.models import TestConsent

from ..classes import BaseSearchByWord
from ..exceptions import SearchModelError, SearchAttributeError


class SearchMethodsTests(TestCase):

    def setUp(self):
        from edc_testing.tests.factories import TestConsentFactory
        self.test_consent_factory = TestConsentFactory

    def test_section_name(self):

        class TestSearchByWord(BaseSearchByWord):
            search_model = TestConsent

        class SectionSubjectView(BaseSectionView):
            section_name = 'subject'
            section_display_name = 'Test Subjects'
            section_display_index = 20
            section_template = 'section_subject.html'
            search = [TestSearchByWord]
        site_sections.register(SectionSubjectView)

        test_search = TestSearchByWord()

        print 'assert returns section name from class variable'
        self.assertEqual(test_search.get_section_name(), 'subject')
        print 'assert returns search model from class variable as model class'
        self.assertTrue(issubclass(test_search.get_search_model_cls(), TestConsent))
        test_search = None
        TestSearchByWord.search_model = ('bhp_base_test', 'TestConsent')
        test_search = TestSearchByWord()
        print 'assert returns search model from class variable as tuple'
        self.assertTrue(issubclass(test_search.get_search_model_cls(), TestConsent))
        TestSearchByWord.search_model = ('bhp_base_testXXXX', 'TestConsent')
        error_test_search = TestSearchByWord()
        print 'assert raises error if cannot get a model class from class variable tuple'
        self.assertRaises(SearchModelError, error_test_search.get_search_model_cls)
        TestSearchByWord.section = None
        TestSearchByWord.search_model = ('bhp_base_test', 'TestConsent')
        error_test_search = TestSearchByWord()
        print 'assert raises exception if class variable section_name not set'
        self.assertRaises(SearchAttributeError, error_test_search.get_section_name)
        print 'create 15 instances in the search model'
        i = 0
        while i < 15:
            self.test_consent_factory()
            i += 1
        print 'get most recent (10)'
        self.assertIsNotNone(test_search.get_most_recent())
        qs = test_search.get_most_recent()
        print 'assert get_most_recent returns a queryset'
        self.assertTrue(isinstance(qs, QuerySet))
        page = test_search._paginate(qs, 1, 10)
        print 'assert _paginate returns a paginator'
        self.assertTrue(isinstance(page, Page))
