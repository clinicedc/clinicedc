from django.apps import apps as django_apps
from edc_model_wrapper import ModelWrapper

from ..dashboard_urls import dashboard_urls

edc_lab_app_config = django_apps.get_app_config('edc_lab')


class ManifestModelWrapper(ModelWrapper):

    model = edc_lab_app_config.manifest_model
    next_url_name = dashboard_urls.get('manifest_listboard_url')
