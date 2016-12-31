from django.core.exceptions import MultipleObjectsReturned
from django.core.paginator import Paginator, EmptyPage

from edc_search.forms import SearchForm


class SearchViewMixin:

    form_class = SearchForm
    template_name = None
    paginate_by = 10
    search_url_name = None
    search_model = None

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
            context.update(form=form, results=results)
        return self.render_to_response(context)
