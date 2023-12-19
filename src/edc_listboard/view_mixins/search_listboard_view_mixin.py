from django.db.models import Q
from django.utils.html import escape
from django.utils.text import slugify


class SearchListboardMixin:
    search_fields = ["slug"]

    default_querystring_attrs = "q"
    alternate_search_attr = "subject_identifier"

    def __init__(self, **kwargs):
        self._search_term = None
        super().__init__(**kwargs)

    def get_context_data(self, **kwargs):
        kwargs.update(search_term=self.search_term)
        return super().get_context_data(**kwargs)

    def get_queryset_filter_options(self, request, *args, **kwargs) -> tuple[Q, dict]:
        """Override to add conditional logic to filter on search term."""
        q_object, options = super().get_queryset_filter_options(request, *args, **kwargs)
        if self.search_term and "|" not in self.search_term:  # TODO: what is this?
            for search_term in self.search_terms:
                for field in self.search_fields:
                    q_object |= Q(**{f"{field}__icontains": slugify(search_term)})
        return q_object, options

    def clean_search_term(self, search_term):
        return search_term

    @property
    def raw_search_term(self):
        raw_search_term = self.request.GET.get(self.default_querystring_attrs)
        if not raw_search_term:
            raw_search_term = self.kwargs.get(self.alternate_search_attr)
        return raw_search_term

    @property
    def search_term(self):
        if not self._search_term:
            search_term = self.raw_search_term
            if search_term:
                search_term = escape(search_term).strip()
            search_term = self.clean_search_term(search_term)
            self._search_term = search_term
        return self._search_term

    @property
    def search_terms(self):
        # TODO: what is this?
        return self.search_term.split("+")
