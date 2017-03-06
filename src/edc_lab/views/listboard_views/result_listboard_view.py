from django.apps import apps as django_apps
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from edc_dashboard.wrappers.model_wrapper import ModelWrapper

from .base_listboard import BaseListboardView


app_name = 'edc_lab'
app_config = django_apps.get_app_config(app_name)


class ResultModelWrapper(ModelWrapper):

    model_name = app_config.result_model


class ResultListboardView(BaseListboardView):

    app_config_name = 'edc_lab'
    navbar_item_selected = 'result'

    listboard_url_name = app_config.result_listboard_url_name
    listboard_template_name = app_config.result_listboard_template_name
    model_name = app_config.result_model
    model_wrapper_class = ResultModelWrapper
    form_action_url_name = '{}:aliquot_url'.format(app_name)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_template_names(self):
        return [django_apps.get_app_config(
            self.app_config_name).result_listboard_template_name]
