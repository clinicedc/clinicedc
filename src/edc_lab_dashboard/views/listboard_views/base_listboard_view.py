from django.urls.base import reverse

from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import AppConfigViewMixin, ListboardFilterViewMixin
from edc_dashboard.views import ListboardView
from edc_navbar import NavbarViewMixin

from ..mixins import UrlsViewMixin, ModelsViewMixin


class BaseListboardView(UrlsViewMixin, NavbarViewMixin,
                        ListboardFilterViewMixin,
                        ModelsViewMixin, AppConfigViewMixin,
                        EdcBaseViewMixin, ListboardView):

    app_config_name = 'edc_lab_dashboard'
    navbar_name = 'specimens'

    search_url_name = None
    listboard_url_name = None
    listboard_template_name = None
    action_name = None
    form_action_url_name = None
    form_action_name = 'form_action'
    form_action_selected_items_name = 'selected_items'

    @property
    def search_form_url(self):
        url = reverse(
            self.search_url_name or self.listboard_url_name,
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
    def form_action_url(self):
        return reverse(
            self.form_action_url_name or self.listboard_url_name,
            kwargs=self.form_action_url_kwargs)

    @property
    def listboard_url(self):
        return reverse(
            self.listboard_url_name,
            kwargs=self.url_kwargs)

    def get_template_names(self):
        return [self.listboard_template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            action_name=self.action_name,
            search_form_url=self.search_form_url,
            listboard_url=self.listboard_url,
            form_action_name=self.form_action_name,
            form_action_selected_items_name=self.form_action_selected_items_name,
            form_action_url=self.form_action_url,
        )
        return context
