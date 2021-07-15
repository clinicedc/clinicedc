from django.apps import apps as django_apps
from django.conf import settings


def get_ltfu_model_name():
    return getattr(settings, "EDC_LFTU_MODEL_NAME", "edc_ltfu.ltfu")


def get_ltfu_model_cls():
    return django_apps.get_model(get_ltfu_model_name())
