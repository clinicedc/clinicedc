from django.apps import apps as django_apps
from edc_model_wrapper import ModelWrapper

from ..dashboard_urls import dashboard_urls

edc_lab_app_config = django_apps.get_app_config('edc_lab')


class ResultModelWrapper(ModelWrapper):

    model = edc_lab_app_config.result_model
    next_url_name = dashboard_urls.get('result_listboard_url')
