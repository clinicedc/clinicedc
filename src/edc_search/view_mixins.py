from django.core.exceptions import MultipleObjectsReturned
from django.core.paginator import Paginator, EmptyPage

from edc_search.forms import SearchForm


class SearchViewMixin:

    form_class = SearchForm
    template_name = None
    paginate_by = 10
    search_model = None
    url_lookup_parameters = []
    list_url = '/'

    def __init__(self, **kwargs):
        self.filter_options = {}
        super().__init__(**kwargs)

    def search_options(self, search_term, **kwargs):
        """Override to return options for the search model filter().

        Returns a Q object and additional kwargs for the filter"""
        q = ()
        options = {}
        return q, options

    def queryset_wrapper(self, qs):
        return qs

    def queryset(self, search_term, **kwargs):
        """Returns a queryset matching the search term."""
        q, options = self.search_options(search_term, **kwargs)
        try:
            qs = [self.search_model.objects.get(q, **options)]
        except self.search_model.DoesNotExist:
            qs = None
        except MultipleObjectsReturned:
            qs = self.search_model.objects.filter(q, **options).order_by('-created')
        return qs

    def paginate(self, qs):
        """Paginates a queryset."""
        paginator = Paginator(qs, self.paginate_by)
        paginator.object_list = self.queryset_wrapper(paginator.object_list)
        try:
            page = paginator.page(self.kwargs.get('page', 1))
        except EmptyPage:
            page = paginator.page(paginator.num_pages)
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
        """Returns a queryset filtered by URL parameters from the context."""
        return self.search_model.objects.filter(**self.filter_options).order_by('-created')

    def update_filter_options_from(self, context):
        """Returns options for the filter() of `filtered_results`."""
        lookups = []
        for attrname in self.url_lookup_parameters:
            if isinstance(attrname, tuple):
                lookups.append((attrname[0], attrname[1]))
            else:
                lookups.append((attrname, attrname))
        for attrname, lookup in lookups:
            if context.get(attrname):
                self.filter_options = {lookup: context.get(attrname)}
                context['search_term'] = context.get(attrname)
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.update_filter_options_from(context)
        context.update(
            show_paginator_control=True if self.filtered_results.count() > self.paginate_by else False,
            list_url=self.list_url,
            results=self.paginate(self.filtered_results),
            result_count_total=self.filtered_results.count())
        return context
