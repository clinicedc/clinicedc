from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.forms import SearchForm as BaseSearchForm
from edc_dashboard.view_mixins import AppConfigViewMixin
from edc_dashboard.views import ListboardView
from edc_dashboard.wrappers.model_wrapper import ModelWrapper

from ...forms import PackAliquotsForm


app_config = django_apps.get_app_config('edc_lab')


class AliquotModelWrapper(ModelWrapper):

    model_name = 'edc_lab.aliquot'

    def human_aliquot_identifier(self):
        return self._original_object.human_aliquot_identifier


class SearchForm(BaseSearchForm):
    action_url_name = app_config.aliquot_listboard_url_name


class AliquotListboardView(AppConfigViewMixin,
                           EdcBaseViewMixin,
                           ListboardView):

    app_config_name = 'edc_lab'
    navbar_item_selected = 'pack'
    navbar_name = 'specimens'

    model = django_apps.get_model(*app_config.aliquot_model.split('.'))
    model_wrapper_class = AliquotModelWrapper
    search_form_class = SearchForm
    paginate_by = 10
    show_all = False
    packed = False
    shipped = False
    listboard_url_name = 'edc-lab:aliquot_listboard_url'
    form_action_url_name = 'edc-lab:pack_aliquots_url'
    search_form_action_url_name = None
    empty_queryset_message = 'No aliquots to display'

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
            self.app_config_name).aliquot_listboard_template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app_config.manifest.update_destinations()
        context.update(
            manifest_listboard_url_name=app_config.manifest_listboard_url_name,
            empty_queryset_message=self.empty_queryset_message,
            pack_aliquots_form=PackAliquotsForm(
                initial={'destination': app_config.manifest.default_destination}),
            form_action_url_name=self.form_action_url_name,
            show_all=self.show_all,
            packed=self.packed,
            shipped=self.shipped)
        return context

    def get_queryset_filter_options(self, request, *args, **kwargs):
        """Returns filter options applied to every
        queryset.
        """
        if self.show_all:
            return {}
        return {'packed': self.packed}
