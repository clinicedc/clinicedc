from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from edc_base.view_mixins import EdcBaseViewMixin
from edc_constants.constants import YES
from edc_dashboard.forms import SearchForm as BaseSearchForm
from edc_dashboard.view_mixins import AppConfigViewMixin
from edc_dashboard.views import ListboardView
from edc_dashboard.wrappers.model_wrapper import ModelWrapper


app_config = django_apps.get_app_config('edc_lab')


class RequisitionModelWrapper(ModelWrapper):

    model_name = app_config.requisition_model
    next_url_name = app_config.requisition_listboard_url_name


class SearchForm(BaseSearchForm):
    action_url_name = app_config.requisition_listboard_url_name


class RequisitionListboardView(AppConfigViewMixin, EdcBaseViewMixin,
                               ListboardView):

    app_config_name = 'edc_lab'
    navbar_item_selected = 'receive'
    navbar_name = 'specimens'

    model = django_apps.get_model(*app_config.requisition_model.split('.'))
    model_wrapper_class = RequisitionModelWrapper
    search_form_class = SearchForm
    paginate_by = 10
    show_all = False
    received = False
    processed = False
    packed = False
    shipped = False
    action = None
    action_url_name = None
    search_form_action_url_name = None
    empty_queryset_message = 'No requisitions to display'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @property
    def search_form(self):
        self.search_form_class.action_url_name = (
            self.search_form_action_url_name or app_config.requisition_listboard_url_name)
        return self.search_form_class

    def get_template_names(self):
        return [django_apps.get_app_config(
            self.app_config_name).requisition_listboard_template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            empty_queryset_message=self.empty_queryset_message,
            show_all=self.show_all,
            received=self.received,
            processed=self.processed,
            packed=self.packed,
            shipped=self.shipped,
            action=self.action,
            action_url_name=self.action_url_name)
        return context

    def get_queryset_filter_options(self, request, *args, **kwargs):
        """Returns filter options applied to every
        queryset.
        """
        if self.show_all:
            return {
                'is_drawn': YES}
        return {
            'is_drawn': YES,
            'received': self.received,
            'processed': self.processed,
            'packed': self.packed,
            'shipped': self.shipped}
