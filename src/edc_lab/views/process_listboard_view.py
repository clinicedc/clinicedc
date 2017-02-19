from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from edc_dashboard.forms import SearchForm as BaseSearchForm
from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import AppConfigViewMixin
from edc_dashboard.views import ListboardView
from edc_dashboard.wrappers.model_wrapper import ModelWrapper

from ..models import Aliquot


app_config = django_apps.get_app_config('edc_lab')


class AliquotModelWrapper(ModelWrapper):

    model_name = Aliquot
#     extra_querystring_attrs = {
#         'bcpp_subject.subjectvisit': ['household_member']}
#     next_url_attrs = {'bcpp_subject.subjectvisit': [
#         'appointment', 'household_identifier', 'subject_identifier',
#         'survey_schedule', 'survey']}
#     url_instance_attrs = [
#         'household_identifier', 'subject_identifier', 'survey_schedule', 'survey',
#         'appointment', 'household_member']


class SearchForm(BaseSearchForm):
    action_url_name = app_config.process_listboard_url_name


class ProcessListboardView(AppConfigViewMixin, EdcBaseViewMixin,
                           ListboardView):

    app_config_name = 'edc_lab'
    navbar_item_selected = 'process'
    navbar_name = 'specimens'

    model = Aliquot
    model_wrapper_class = AliquotModelWrapper
    search_form_class = SearchForm
    paginate_by = 10
    show_all = False
    received = True
    processed = False
    packed = False
    shipped = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search_term = None

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_template_names(self):
        return [django_apps.get_app_config(
            self.app_config_name).process_listboard_template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            show_all=self.show_all,
            received=self.received,
            processed=self.processed,
            packed=self.packed,
            shipped=self.shipped)
        return context

    def get_queryset_filter_options(self, request, *args, **kwargs):
        """Returns filter options applied to every
        queryset.
        """
        if self.show_all:
            return {}
        return {
            'received': self.received,
            'processed': self.processed,
            'packed': self.packed,
            'shipped': self.shipped}
