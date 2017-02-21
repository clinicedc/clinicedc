from django.apps import apps as django_apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from edc_dashboard.forms import SearchForm as BaseSearchForm
from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import AppConfigViewMixin
from edc_dashboard.views import ListboardView
from edc_dashboard.wrappers.model_wrapper import ModelWrapper


app_config = django_apps.get_app_config('edc_lab')


class BoxModelWrapper(ModelWrapper):

    model_name = app_config.box_model
    next_url_name = app_config.pack_listboard_url_name


class SearchForm(BaseSearchForm):
    action_url_name = app_config.pack_listboard_url_name


class PackListboardView(AppConfigViewMixin, EdcBaseViewMixin,
                        ListboardView):

    action = None
    action_url_name = None
    app_config_name = 'edc_lab'
    empty_queryset_message = 'No boxes to display'
    listboard_url_name = app_config.pack_listboard_url_name
    model = django_apps.get_model(*app_config.box_model.split('.'))
    model_wrapper_class = BoxModelWrapper
    navbar_item_selected = 'pack'
    navbar_name = 'specimens'
    paginate_by = 10
    search_form_action_url_name = app_config.pack_listboard_url_name
    search_form_action_url_name = None
    search_form_class = SearchForm
    shipped = None

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @property
    def search_form(self):
        self.search_form_class.action_url_name = (
            self.search_form_action_url_name or app_config.pack_listboard_url_name)
        return self.search_form_class

    def get_template_names(self):
        return [django_apps.get_app_config(
            self.app_config_name).pack_listboard_template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            messages=messages,
            box_listboard_url_name=app_config.box_listboard_url_name,
            new_box=BoxModelWrapper.new(),
            empty_queryset_message=self.empty_queryset_message,
            shipped=self.shipped,
            action=self.action,
            action_url_name=self.action_url_name)
        return context
