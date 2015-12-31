from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured

from edc_testing.models import TestModel
from edc.dashboard.search.classes import BaseSearchByWord

from ..classes import BaseSectionIndexView
from ..classes import site_sections, BaseSectionView


class TestModelSearchByWord(BaseSearchByWord):
    search_model = TestModel
    order_by = 'created'
    template = 'search_plot_result_include.html'


class TestSectionOneView(BaseSectionView):
    section_name = 'test_one'
    section_display_name = 'Thing One'
    section_display_index = 110
    search_cls = TestModelSearchByWord
    add_model = TestModel


class TestSectionTwoView(BaseSectionView):
    section_name = 'test_two'
    section_display_name = 'Thing Two'
    section_display_index = 110  # set to same as above to trigger exception


class TestSectionThreeView(BaseSectionView):
    section_name = 'test_three'
    section_display_name = 'Thing Three'
    section_display_index = 100


class SectionControllerTests(TestCase):

    def setUp(self):
        site_sections.register(TestSectionOneView)
        site_sections.register(TestSectionTwoView)

    def tearDown(self):
        site_sections.unregister('test_one')
        site_sections.unregister('test_two')
        site_sections.unregister('test_three')

    def test_controller(self):
        self.assertEqual(site_sections.get_section_names(), ['test_one', 'test_two'])
        self.assertEqual(site_sections.get_section_display_names(), ['Thing One', 'Thing Two'])
        self.assertEqual(site_sections.get_section_list(), site_sections.get_section_tuples())
        self.assertEqual(sorted([tpl.section_name for tpl in site_sections.get_section_tuples()]), sorted(site_sections.get_section_names()))
        self.assertEqual(sorted([tpl.display_name for tpl in site_sections.get_section_tuples()]), sorted(site_sections.get_section_display_names()))
        self.assertRaises(ImproperlyConfigured, site_sections.get_section_display_indexes)
        site_sections.unregister('test_two')
        site_sections.register(TestSectionThreeView)
        self.assertEqual(site_sections.get_section_display_indexes(), [100, 110])
        self.assertEqual(site_sections.get_section_names(), ['test_one', 'test_three'])
        self.assertEqual(site_sections.get_section_display_names(), ['Thing One', 'Thing Three'])
        self.assertEqual(site_sections.get_indexed_section_display_names(), ['Thing Three', 'Thing One'])
        self.assertEqual(site_sections.get_section_list(), site_sections.get_section_tuples())
        self.assertEqual(sorted([tpl.section_name for tpl in site_sections.get_section_tuples()]), sorted(site_sections.get_section_names()))
        self.assertEqual(sorted([tpl.display_name for tpl in site_sections.get_section_tuples()]), sorted(site_sections.get_section_display_names()))

        site_sections.autodiscover()
        self.assertTrue(site_sections.is_autodiscovered)

        section_index_view = BaseSectionIndexView()
        self.assertEqual(section_index_view.get_section_display_name_list(), ['Thing One', 'Thing Three'])
        self.assertEqual(section_index_view.get_indexed_section_display_name_list(), ['Thing Three', 'Thing One'])
        self.assertFalse(section_index_view.is_setup)
        section_index_view.setup()
        self.assertTrue(section_index_view.is_setup)
