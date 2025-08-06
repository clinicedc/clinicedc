from django.apps import apps as django_apps
from django.conf import settings


def get_ltfu_model_name():
    model_name = getattr(settings, "EDC_LTFU_MODEL_NAME", None)
    if not model_name:
        raise ValueError("Model name may not be none. Got EDC_LTFU_MODEL_NAME=''")
    return getattr(settings, "EDC_LTFU_MODEL_NAME", None)


def get_ltfu_model_cls():
    return django_apps.get_model(get_ltfu_model_name())
