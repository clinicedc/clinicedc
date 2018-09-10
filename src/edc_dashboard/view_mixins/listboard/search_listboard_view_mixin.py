from django.utils.html import escape
from django.db.models import Q
from django.utils.text import slugify


class SearchListboardMixin:

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._search_term = None

    def extra_search_options(self, search_term):
        """Returns a search Q object that will be added to the
        search criteria (OR) for the search queryset.
        """
        return Q()

    def clean_search_term(self, search_term):
        return search_term

    @property
    def search_term(self):
        if not self._search_term:
            search_term = self.request.GET.get('q')
            if search_term:
                search_term = escape(search_term).strip()
            search_term = self.clean_search_term(search_term)
            self._search_term = search_term
        return self._search_term

    def get_queryset_for_listboard(self, filter_options=None, exclude_options=None):
        """Override to add conditional logic to filter on search term.
        """
        if self.search_term and '|' not in self.search_term:
            search_terms = self.search_term.split('+')
            q = None
            q_objects = []
            for search_term in search_terms:
                q_objects.append(Q(slug__icontains=slugify(search_term)))
                q_objects.append(self.extra_search_options(search_term))
            for q_object in q_objects:
                if q:
                    q = q | q_object
                else:
                    q = q_object
            queryset = self.listboard_model_cls.objects.filter(
                q or Q(), **filter_options).exclude(**exclude_options)
        else:
            queryset = super().get_queryset_for_listboard(
                filter_options=filter_options,
                exclude_options=exclude_options)
        return queryset
