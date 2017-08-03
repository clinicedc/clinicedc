from django.apps import apps as django_apps
from edc_model_wrapper import ModelWrapper

app_config = django_apps.get_app_config('edc_lab_dashboard')
edc_lab_app_config = django_apps.get_app_config('edc_lab')


class RequisitionModelWrapper(ModelWrapper):

    model = edc_lab_app_config.requisition_model
    next_url_name = app_config.requisition_listboard_url_name
