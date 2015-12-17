from django.test.client import Client
from django.test import SimpleTestCase
from django.core.urlresolvers import reverse, NoReverseMatch

from edc.testing.models import TestModel
from edc.dashboard.search.classes import BaseSearchByWord

from ..classes import site_sections, BaseSectionView


class TestModelSearchByWord(BaseSearchByWord):
    search_model = TestModel
    order_by = 'created'
    template = 'search_plot_result_include.html'


class SectionOneView(BaseSectionView):
    section_name = 'one'
    section_display_name = 'Thing One'
    section_display_index = 990
    search_cls = TestModelSearchByWord
    add_model = TestModel


class SectionMethodTests(SimpleTestCase):

    def test_section_knows_section_name(self):
        section_one_view = SectionOneView()
        self.assertEquals('one', section_one_view.get_section_name())

    def test_section_knows_search_cls(self):
        section_one_view = SectionOneView()
        self.assertEquals(TestModelSearchByWord, section_one_view.get_search_cls())

    def test_section_knows_add_model(self):
        section_one_view = SectionOneView()
        self.assertEquals(TestModel, section_one_view.get_add_model_cls())

    def test_urlpatterns(self):
        section_one_view = SectionOneView()
        self.assertIn('section_search_url', [p.name for p in section_one_view.urlpatterns()])
        self.assertIn('section_url', [p.name for p in section_one_view.urlpatterns()])

    def test_url_reverse(self):
        section_one_view = SectionOneView()
        site_sections.register(SectionOneView)
        self.assertTrue(isinstance(reverse('section_url', kwargs={'section_name': section_one_view.get_section_name()}), basestring))
        self.assertRaises(NoReverseMatch, reverse, 'section_url', kwargs={'section_name': ''})
        self.assertTrue(isinstance(reverse('section_search_url', kwargs={'section_name': section_one_view.get_section_name(), 'search_term': '123'}), basestring))
        self.assertTrue(isinstance(reverse('section_search_url', kwargs={'section_name': section_one_view.get_section_name(), 'search_term': None}), basestring))
        site_sections.unregister(SectionOneView)

    def test_search(self):
        section_one_view = SectionOneView()
#        section_one_view.get_search_result(request)
