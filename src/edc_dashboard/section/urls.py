from .classes import site_sections, SectionIndexView

section_index_view = SectionIndexView()
section_index_view.prepare()
urlpatterns = []
for section in site_sections.all().itervalues():
    section.section_list = section_index_view.section_list
    urlpatterns += section.urlpatterns()
urlpatterns += section_index_view.urlpatterns()
