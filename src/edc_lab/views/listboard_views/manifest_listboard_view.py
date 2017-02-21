from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from edc_dashboard.forms import SearchForm as BaseSearchForm
from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import AppConfigViewMixin
from edc_dashboard.views import ListboardView
from edc_dashboard.wrappers.model_wrapper import ModelWrapper


app_config = django_apps.get_app_config('edc_lab')


class ManifestModelWrapper(ModelWrapper):

    model_name = app_config.manifest_model
    next_url_name = app_config.manifest_listboard_url_name

    def aliquots(self):
        return self._original_object.aliquot_set.all().order_by('count')


class SearchForm(BaseSearchForm):
    action_url_name = app_config.manifest_listboard_url_name


class ManifestListboardView(AppConfigViewMixin, EdcBaseViewMixin,
                            ListboardView):

    app_config_name = 'edc_lab'
    navbar_item_selected = 'manifest'
    navbar_name = 'specimens'

    model = django_apps.get_model(*app_config.manifest_model.split('.'))
    aliquot_model = django_apps.get_model(*app_config.aliquot_model.split('.'))
    model_wrapper_class = ManifestModelWrapper
    search_form_class = SearchForm
    paginate_by = 10
    action = None
    action_url_name = None

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_template_names(self):
        return [app_config.manifest_listboard_template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            requisition_listboard_url_name=app_config.requisition_listboard_url_name,
            aliquot_listboard_url_name=app_config.aliquot_listboard_url_name,
            action=self.action,
            action_url_name=self.action_url_name)
        return context
