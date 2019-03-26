from django.apps import apps as django_apps
from edc_lab.models import Manifest
from edc_model_wrapper import ModelWrapper

edc_lab_app_config = django_apps.get_app_config("edc_lab")


class ManifestModelWrapper(ModelWrapper):

    model_cls = Manifest
    next_url_name = "manifest_listboard_url"
