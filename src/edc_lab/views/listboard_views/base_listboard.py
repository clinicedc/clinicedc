from django.apps import apps as django_apps
from django.contrib import messages
from django.urls.base import reverse

from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.forms import SearchForm
from edc_dashboard.view_mixins import AppConfigViewMixin
from edc_dashboard.views import ListboardView

from ..mixins import UrlsViewMixin, ModelsViewMixin

app_name = 'edc_lab'
app_config = django_apps.get_app_config(app_name)


class BaseListboardView(UrlsViewMixin, ModelsViewMixin, AppConfigViewMixin,
                        EdcBaseViewMixin, ListboardView):

    app_config_name = app_name
    navbar_name = 'specimens'

    search_form_class = SearchForm
    search_url_name = None
    listboard_url_name = None
    listboard_template_name = None
    action_name = None
    form_action_url_name = None
    form_action_name = 'form_action'
    form_action_selected_items_name = 'selected_items'

    @property
    def search_form(self):
        self.search_form_class.action_url = reverse(
            self.search_url_name or self.listboard_url_name,
            kwargs=self.search_url_kwargs)
        return self.search_form_class

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

    def get_template_names(self):
        return [self.listboard_template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            action_name=self.action_name,
            # messages=messages,
            form_action_name=self.form_action_name,
            form_action_selected_items_name=self.form_action_selected_items_name,
            form_action_url=self.form_action_url,
        )
        return context
