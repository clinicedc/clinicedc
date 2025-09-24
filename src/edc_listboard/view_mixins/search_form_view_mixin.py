from typing import Any

from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch

from edc_dashboard.url_names import url_names


class SearchFormViewError(Exception):
    pass


class SearchFormViewMixin:
    search_form_url = None

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        kwargs.update(search_form_url_reversed=self.search_form_url_reversed)
        return super().get_context_data(**kwargs)

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
                f"{e}. Expected one of {url_names.registry}. See attribute 'search_form_url'."
            ) from e
        return f"{url}{self.querystring}"

    @property
    def search_form_url_kwargs(self):
        """Override to add custom kwargs to reverse the search form url."""
        return self.url_kwargs
