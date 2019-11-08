from django.apps import apps as django_apps
from django.conf import settings


def get_randomizationlist_model_name():
    model_name = getattr(
        settings, "EDC_RANDOMIZATIONLIST_MODEL", "edc_randomization.randomizationlist"
    )
    return model_name


def get_randomizationlist_model():
    model = getattr(
        settings, "EDC_RANDOMIZATIONLIST_MODEL", "edc_randomization.randomizationlist"
    )
    return django_apps.get_model(model)


def get_historicalrandomizationlist_model():
    model = getattr(
        settings, "EDC_RANDOMIZATIONLIST_MODEL", "edc_randomization.randomizationlist"
    )
    return django_apps.get_model(model).history.model
