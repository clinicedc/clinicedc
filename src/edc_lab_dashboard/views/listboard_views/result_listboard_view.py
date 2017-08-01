from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from edc_model_wrapper import ModelWrapper

from .base_listboard import BaseListboardView


app_config = django_apps.get_app_config('edc_lab_dashboard')
edc_lab_app_config = django_apps.get_app_config('edc_lab')


class ResultModelWrapper(ModelWrapper):

    model = edc_lab_app_config.result_model


class ResultListboardView(BaseListboardView):

    app_config_name = 'edc_lab_dashboard'
    navbar_item_selected = 'result'

    listboard_url_name = app_config.result_listboard_url_name
    listboard_template_name = app_config.result_listboard_template_name
    model = edc_lab_app_config.result_model
    model_wrapper_cls = ResultModelWrapper
    form_action_url_name = f'edc_lab_dashboard:aliquot_url'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
