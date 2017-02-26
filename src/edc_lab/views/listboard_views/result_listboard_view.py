from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import AppConfigViewMixin
from edc_dashboard.views import ListboardView
from edc_dashboard.wrappers.model_wrapper import ModelWrapper


app_config = django_apps.get_app_config('edc_lab')


class ResultModelWrapper(ModelWrapper):

    model_name = app_config.result_model


class ResultListboardView(AppConfigViewMixin, EdcBaseViewMixin,
                          ListboardView):

    app_config_name = 'edc_lab'
    navbar_item_selected = 'result'
    navbar_name = 'specimens'

    model = django_apps.get_model(*app_config.result_model.split('.'))
    model_wrapper_class = ResultModelWrapper
    paginate_by = 10
    show_all = False
    resulted = False
    form_action_url_name = None

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_template_names(self):
        return [django_apps.get_app_config(
            self.app_config_name).result_listboard_template_name]
