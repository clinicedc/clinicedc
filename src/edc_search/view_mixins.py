from django.core.exceptions import MultipleObjectsReturned

from edc_search.forms import SearchForm


class SearchViewMixin:

    form_class = SearchForm
    template_name = None
    paginate_by = 10
    search_url_name = None
    search_model = None

    def search_options(self, search_term, **kwargs):
        q = ()
        options = {}
        return q, options

    def queryset_wrapper(self, qs):
        return qs

    def queryset(self, search_term, **kwargs):
        q, options = self.search_options(search_term, **kwargs)
        try:
            qs = [self.search_model.objects.get(q, **options)]
        except self.search_model.DoesNotExist:
            qs = None
        except MultipleObjectsReturned:
            qs = self.search_model.objects.filter(q, **options).order_by('-created')
        return self.queryset_wrapper(qs)

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
            context = self.get_context_data()
            context.update(form=form, results=results)
        return self.render_to_response(context)
