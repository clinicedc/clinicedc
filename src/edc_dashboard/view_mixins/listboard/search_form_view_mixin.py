from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch
from django.views.generic.base import ContextMixin
from edc_dashboard.url_names import url_names


class SearchFormViewError(Exception):
    pass


class SearchFormViewMixin(ContextMixin):

    search_form_url = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(search_form_url_reversed=self.search_form_url_reversed)
        return context

    @property
    def search_form_url_reversed(self):
        """Returns the reversed url selected from the url_names
        using self.search_form_url.
        """
        try:
            url = reverse(
                url_names.get(self.search_form_url), kwargs=self.search_form_url_kwargs
            )
        except NoReverseMatch as e:
            raise SearchFormViewError(
                f"{e}. Expected one of {url_names.registry}. "
                f"See attribute 'search_form_url'."
            )
        return f"{url}{self.querystring}"

    @property
    def search_form_url_kwargs(self):
        """Override to add custom kwargs to reverse the search form url.
        """
        return self.url_kwargs
