from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from ...model_wrappers import ResultModelWrapper
from .base_listboard_view import BaseListboardView


app_config = django_apps.get_app_config('edc_lab_dashboard')
edc_lab_app_config = django_apps.get_app_config('edc_lab')


class ResultListboardView(BaseListboardView):

    app_config_name = 'edc_lab_dashboard'
    navbar_selected_item = 'result'

    listboard_url = 'result_listboard_url'
    listboard_template = 'result_listboard_template'
    model = edc_lab_app_config.result_model
    model_wrapper_cls = ResultModelWrapper
    form_action_url = 'aliquot_action_url'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
