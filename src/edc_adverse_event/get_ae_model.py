from django.apps import apps as django_apps
from django.conf import settings


def get_ae_model(model_name):
    return django_apps.get_model(f"{settings.ADVERSE_EVENT_APP_LABEL}.{model_name}")


def get_ae_model_name(model_name):
    return f"{settings.ADVERSE_EVENT_APP_LABEL}.{model_name}"
