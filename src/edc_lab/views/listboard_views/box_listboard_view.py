from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.urls.base import reverse
from django.utils.decorators import method_decorator

from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.forms import SearchForm as BaseSearchForm
from edc_dashboard.view_mixins import AppConfigViewMixin
from edc_dashboard.views import ListboardView
from edc_dashboard.wrappers.model_wrapper import ModelWrapper


app_config = django_apps.get_app_config('edc_lab')


class BoxItemModelWrapper(ModelWrapper):

    model_name = app_config.box_item_model
    next_url_name = app_config.box_listboard_url_name
    next_url_attrs = {
        'edc_lab.boxitem': ['box_identifier']}
    url_instance_attrs = ['box_identifier']

    def human_readable_identifier(self):
        return self._original_object.human_readable_identifier

    def box_identifier(self):
        return self._original_object.box.box_identifier


class SearchForm(BaseSearchForm):

    action_url_name = app_config.box_listboard_url_name


class BoxListboardView(AppConfigViewMixin, EdcBaseViewMixin,
                       ListboardView):

    action = None
    action_url_name = None
    app_config_name = 'edc_lab'
    empty_queryset_message = 'No items have been added to this box'
    listboard_url_name = app_config.box_listboard_url_name
    model = django_apps.get_model(*app_config.box_item_model.split('.'))
    model_wrapper_class = BoxItemModelWrapper
    navbar_item_selected = 'pack'
    navbar_name = 'specimens'
    paginate_by = 10
    search_form_action_url_name = app_config.box_listboard_url_name
    search_form_class = SearchForm
    ordering = ('-position', )

    add_boxitem_url_name = 'edc-lab:add_boxitem_url'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @property
    def search_form(self):
        self.search_form_class.action_url_name = (
            self.search_form_action_url_name or app_config.box_listboard_url_name)
        return self.search_form_class

    def get_template_names(self):
        return [django_apps.get_app_config(
            self.app_config_name).box_listboard_template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            listboard_url=reverse(
                django_apps.get_app_config('edc_lab').box_listboard_url_name,
                kwargs={'box_identifier': self.kwargs.get('box_identifier')}),
            pack_listboard_url_name=app_config.pack_listboard_url_name,
            box_identifier=self.kwargs.get('box_identifier'),
            add_boxitem_url_name=self.add_boxitem_url_name,
            empty_queryset_message=self.empty_queryset_message,
            action=self.action,
            action_url_name=self.action_url_name)
        return context
