import arrow

from arrow.parser import ParserError

from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Q

from edc_dashboard.paginator_mixin import PaginatorMixin
from edc_search.forms import SearchForm
from django.views.generic.edit import FormView
from pprint import pprint


class SearchViewMixin(PaginatorMixin, FormView):

    """Adds a search form that inserts a paginated list of wrapped
    models into the context.

    Declare with a FormView.
    """

    form_class = SearchForm
    search_model = None
    search_queryset_ordering = '-created'
    search_model_wrapper_class = None

    def get_form_class(self):
        self.form_class = super().get_form_class()
        self.form_class.listboard_url_name = self.listboard_url_name
        self.form_class.navbars = self.navbars
        return self.form_class

    def get_search_options(self, search_term, **kwargs):
        q = Q()
        options = {}
        try:
            search_term = arrow.get(search_term)
        except (ParserError, ValueError):
            try:
                field, value = search_term.split('=')
                options = {field: value}
            except ValueError:
                q, options = self.search_options(search_term, **kwargs)
        else:
            q, options = self.search_options_for_date(search_term, **kwargs)
        return q, options

    def search_options_for_date(self, search_term, **kwargs):
        """Returns a Q set and empty options to search on date
        part of datetime.

        search term assumed to be an arrow object and will be converted
        to UTC.
        """
        q = (Q(modified__date=search_term.to('utc').date()) |
             Q(created__date=search_term.to('utc').date()))
        return q, {}

    def search_options(self, search_term, **kwargs):
        q = (Q(user_modified=search_term) |
             Q(user_created=search_term) |
             Q(hostname_created=search_term) |
             Q(hostname_modified=search_term))
        return q, {}

    def form_valid(self, form):
        if form.is_valid():
            search_term = form.cleaned_data['search_term']
            results = None
            if search_term:
                search_term = search_term.strip()
                qs = self.search_queryset(search_term, **self.kwargs)
                if not qs:
                    form.add_error(
                        'search_term', 'No matching records for \'{}\'.'.format(
                            search_term))
                else:
                    results = self.paginate(
                        queryset=qs,
                        model_wrapper_class=self.search_model_wrapper_class)
            else:
                results = self.paginate(
                    queryset=self.search_model.objects.all().order_by(
                        '-created'),
                    model_wrapper_class=self.search_model_wrapper_class)
            context = self.get_context_data()
            context.update(
                form=form, results=results, search_term=search_term,
                navbar=form.navbars.get('default'))
        return self.render_to_response(context)

    def search_queryset(self, search_term, **kwargs):
        """Returns a queryset matching the search term passed
        in through the form, see `form_valid`.
        """
        q, options = self.get_search_options(search_term, **kwargs)
        qs = self.search_model.objects.filter(
            q, **options).order_by(self.search_queryset_ordering)
        return qs
