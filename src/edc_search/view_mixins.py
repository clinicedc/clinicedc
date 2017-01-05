import arrow

from django.core.exceptions import MultipleObjectsReturned
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q

from edc_search.forms import SearchForm
from arrow.parser import ParserError


class SearchViewMixin:

    form_class = SearchForm
    list_url = '/'
    paginate_by = 10
    search_model = None
    template_name = None
    url_lookup_parameters = []
    queryset_ordering = '-created'

    def __init__(self, **kwargs):
        self.filter_options = {}
        super().__init__(**kwargs)

    def get_search_options(self, search_term, **kwargs):
        q = Q()
        options = {}
        try:
            search_term = arrow.get(search_term)
        except ParserError:
            try:
                field, value = search_term.split('=')
                options = {field: value}
            except ValueError:
                q, options = self.search_options(search_term, **kwargs)
        else:
            q, options = self.search_options_for_date(search_term, **kwargs)
        return q, options

    def search_options_for_date(self, search_term, **kwargs):
        q = (Q(modified__date=search_term.to('utc').date()) |
             Q(created__date=search_term.to('utc').date()))
        return q, {}

    def search_options(self, search_term, **kwargs):
        q = (Q(user_modified=search_term) |
             Q(user_created=search_term) |
             Q(hostname_created=search_term) |
             Q(hostname_modified=search_term))
        return q, {}

    def queryset_wrapper(self, qs):
        """Wraps either the search queryset or the filtered queryset objects."""
        return qs

    def queryset(self, search_term, **kwargs):
        """Returns a queryset matching the search term passed in through the form, see `form_valid`."""
        q, options = self.get_search_options(search_term, **kwargs)
        try:
            qs = [self.search_model.objects.get(q, **options)]
        except (self.search_model.DoesNotExist, ValueError):
            qs = None
        except MultipleObjectsReturned:
            qs = self.search_model.objects.filter(q, **options).order_by(self.queryset_ordering)
        return qs

    def paginate(self, qs):
        """Paginates a queryset."""
        paginator = Paginator(qs, self.paginate_by)
        try:
            page = paginator.page(self.kwargs.get('page', 1))
        except EmptyPage:
            page = paginator.page(paginator.num_pages)
        page.object_list = self.queryset_wrapper(page.object_list)
        return page

    def form_valid(self, form):
        if form.is_valid():
            search_term = form.cleaned_data['search_term']
            results = None
            if search_term:
                qs = self.queryset(search_term, **self.kwargs)
                if not qs:
                    form.add_error('search_term', 'No matching records for \'{}\'.'.format(search_term))
                else:
                    results = self.paginate(qs)
            else:
                results = self.paginate(self.search_model.objects.all().order_by('-created'))
            context = self.get_context_data()
            context.update(form=form, results=results, search_term=search_term)
        return self.render_to_response(context)

    @property
    def filtered_results(self):
        """Returns a queryset filtered by values from the context, see `update_filter_options_from`.

        This is not the "search" queryset"""
        return self.search_model.objects.filter(**self.filter_options).order_by('-created')

    def update_filter_options_from(self, context):
        """Intercepts from the context and returns options for the `filtered_results`.

        url_lookup_parameters correspond with parameters defined in urls.py"""
        lookups = []
        self.filter_options = {}
        for attrname in self.url_lookup_parameters:
            if isinstance(attrname, tuple):
                lookups.append((attrname[0], attrname[1]))
            else:
                lookups.append((attrname, attrname))
        for attrname, lookup in lookups:
            if context.get(attrname):
                self.filter_options.update({lookup: context.get(attrname)})
                # TODO: ??
                context['search_term'] = context.get(attrname)
        return context

    def get_context_data(self, **kwargs):
        """Updates the context with the paginated filtered results and a few other simple attrs.

        Results are filtered according to the `updated_filter_options_from` the context."""
        context = super().get_context_data(**kwargs)
        context = self.update_filter_options_from(context)
        context.update(
            show_paginator_control=True if self.filtered_results.count() > self.paginate_by else False,
            list_url=self.list_url,
            results=self.paginate(self.filtered_results),
            result_count_total=self.filtered_results.count())
        return context
