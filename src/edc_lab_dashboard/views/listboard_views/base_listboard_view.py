from django.urls.base import reverse

from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import ListboardFilterViewMixin
from edc_dashboard.views import ListboardView
from edc_navbar import NavbarViewMixin

from ...dashboard_urls import dashboard_urls
from ..mixins import ModelsViewMixin


class BaseListboardView(NavbarViewMixin, ListboardFilterViewMixin, ModelsViewMixin,
                        EdcBaseViewMixin, ListboardView):

    action_name = None
    form_action_name = 'form_action'
    form_action_selected_items_name = 'selected_items'
    form_action_url = None
    navbar_name = 'specimens'
    search_url = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            action_name=self.action_name,
            search_form_url_reversed=self.search_form_url_reversed,
            form_action_name=self.form_action_name,
            form_action_selected_items_name=self.form_action_selected_items_name,
            form_action_url_reversed=self.form_action_url_reversed)
        return context

    @property
    def search_form_url_reversed(self):
        url = reverse(
            dashboard_urls.get(self.search_url) or dashboard_urls.get(
                self.listboard_url),
            kwargs=self.search_url_kwargs)
        return f'{url}{self.querystring}'

    @property
    def search_url_kwargs(self):
        return self.url_kwargs

    @property
    def form_action_url_kwargs(self):
        return self.url_kwargs

    @property
    def url_kwargs(self):
        return {}

    @property
    def form_action_url_reversed(self):
        return reverse(
            dashboard_urls.get(self.form_action_url) or dashboard_urls.get(
                self.listboard_url),
            kwargs=self.form_action_url_kwargs)
