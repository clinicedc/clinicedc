from django.conf import settings
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import render_to_response
from django.template import RequestContext

from .most_recent_query import MostRecentQuery


class BaseSectionView(object):

    section_name = None
    section_display_name = None
    section_display_index = None
    section_template = None
    add_model = None
    search = None
    default_search = None
    show_most_recent = False

    def __init__(self):
        self.context = {}
        self.section_list = None
        self.section_template = self.section_template or 'section_{0}.html'.format(self.section_name)
        if not self.search:
            self.search = {}

    def update_context(self, **kwargs):
        """Updates the template context."""
        for k, v in kwargs.iteritems():
            self.context[k] = v

    @property
    def protocol_lab_section(self):
        if 'LAB_SECTION' in dir(settings):
            return settings.LAB_SECTION
        else:
            return ''

    def section_url_patterns(self, view):
        return patterns('',
            url(r'^(?P<section_name>{section_name})/$'.format(section_name=self.section_name),
                view,
                name="section_url"))

    def urlpatterns(self, view=None):
        """ Generates urlpatterns for the view of this section.

        If search classes have been added to this section class, search urls will be added before the section urls.
        """
        if view is None:
            view = self._view
        url_patterns = []
        url_patterns += self.search_url_patterns(view)
        url_patterns += self.section_url_patterns(view)
        return url_patterns

    def _contribute_to_context_wrapper(self, request, *args, **kwargs):
        """Wraps :func:`contribute_to_context`."""
        self.context = self.contribute_to_context(self.context, request, *args, **kwargs)

    def contribute_to_context(self, context, request, *args, **kwargs):
        """Users may override to update the template context with {key, value} pairs."""
        return context

    def _paginate(self, search_result, page, results_per_page=None):
        """Paginates the search result queryset after which templates
        access search_result.object_list.

        Also sets the 'magic_url' for previous/next paging urls

        Keyword Arguments:
            results_per_page: (default: 25)
        """
        if not results_per_page:
            results_per_page = 25
        if search_result:
            paginator = Paginator(search_result, results_per_page)
            try:
                search_result = paginator.page(page)
            except (EmptyPage, InvalidPage):
                search_result = paginator.page(paginator.num_pages)
        return search_result

    def view(self, request, *args, **kwargs):
        """Default view for this section called by :func:`_view`.

        May be overridden
        """
        return render_to_response(self.section_template, self.context, context_instance=RequestContext(request))

    def _view(self, request, *args, **kwargs):
        """Wraps :func:`view` method to force login and treat this like a class based view."""
        @login_required
        def view(request, *args, **kwargs):
            self.context = {}
            try:
                page = int(request.GET.get('page', '1'))
            except ValueError:
                page = 1
            if self.search:
                self.searcher = self.search.get(kwargs.get('search_name', 'word'))()
                self.searcher.search_form_data = request.POST or {'search_term': kwargs.get('search_term')}
                if self.searcher.search_form(self.searcher.search_form_data).is_valid():
                    self.context.update({
                        'search_result': self._paginate(self.searcher.search_result, page),
                        'search_result_include_file': self.searcher.search_result_include_template,
                        })
                else:
                    if self.show_most_recent:
                        self.context.update({
                            'search_result': self._paginate(MostRecentQuery(self.searcher.search_model).query(), page),
                            'search_result_include_file': self.searcher.search_result_include_template,
                            })
            self.context.update({
                'app_name': settings.APP_NAME,
                'installed_apps': settings.INSTALLED_APPS,
                'selected_section': self.section_name,
                'sections': self.section_list,
                'sections_names': [sec[0] for sec in self.section_list],
                'section_name': self.section_name,
                'protocol_lab_section': self.protocol_lab_section,
                })
            try:
                self.context.update({
                    'add_model': self.add_model,
                    'add_model_opts': self.add_model._meta,
                    'add_model_name': self.add_model._meta.verbose_name,
                    })
            except AttributeError:
                pass
            self._contribute_to_context_wrapper(self.context, request, **kwargs)
            if self.search:
                self.searcher.contribute_to_context(self.context)
            return self.view(request, *args, **kwargs)
        return view(request, *args, **kwargs)

    def search_url_patterns(self, view):
        url_patterns = []
        for searcher in self.search.itervalues():
            url_patterns += searcher().url_patterns(view, self.section_name)
        return url_patterns
