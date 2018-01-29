from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch
from django.views.generic.base import ContextMixin


class SearchFormViewError(Exception):
    pass


class SearchFormViewMixin(ContextMixin):

    search_form_url = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            search_form_url_reversed=self.search_form_url_reversed)
        return context

    @property
    def search_form_url_reversed(self):
        """Returns the reversed url selected from the request.url_name_data
        using self.search_form_url.
        """
        try:
            url = reverse(
                self.request.url_name_data.get(self.search_form_url),
                kwargs=self.search_form_url_kwargs)
        except NoReverseMatch as e:
            raise SearchFormViewError(
                f'{e}. Expected one of {list(self.request.url_name_data.keys())}. '
                f'See attribute \'search_form_url\'.')
        return f'{url}{self.querystring}'

    @property
    def search_form_url_kwargs(self):
        """Override to add custom kwargs to reverse the search form url.
        """
        return self.url_kwargs
