from .controller import site_sections


class BaseSectionIndexView(object):

    """ Base section class. """

    def __init__(self):
        """
        Keyword Arguments:
            search_result_template --
            section_name --
        """
        self.indexed_section_tuples = None
        self.section_tuples = None
        self.section_list = None
        self.section_name_list = None
        self.section_display_name_list = None
        self.indexed_section_display_name_list = None
        self.selected_section = None
        self.prepared = False

    def prepare(self):
        if not self.prepared:
            site_sections.autodiscover()
            self.prepared = True
            # an ordered (by display index) list of section tuples that apply to this section class' urlpatterns."""
            self.indexed_section_tuples = site_sections.indexed_section_tuples
            self.section_tuples = self.indexed_section_tuples
            self.section_list = self.indexed_section_tuples
            self.section_name_list = [tpl.section_name for tpl in self.section_tuples]
            self.section_display_name_list = [tpl.display_name for tpl in self.section_tuples]
            self.section_display_name_list.sort()
            self.indexed_section_display_name_list = [tpl.display_name for tpl in self.indexed_section_tuples]
            self.selected_section = None
