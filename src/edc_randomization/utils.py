import os
import sys

from django.apps import apps as django_apps
from django.conf import settings
from django.core.management.color import color_style

style = color_style()


def get_randomizationlist_model_name():
    return settings.EDC_RANDOMIZATION_LIST_MODEL


def get_randomizationlist_model(apps=None):
    model = get_randomizationlist_model_name()
    return (apps or django_apps).get_model(model)


def get_historicalrandomizationlist_model(apps=None):
    model = get_randomizationlist_model_name()
    return (apps or django_apps).get_model(model).history.model


def get_randomization_list_path():
    try:
        path = settings.EDC_RANDOMIZATION_LIST_FILE
    except AttributeError:
        sys.stdout.write(
            style.ERROR(
                "settings.EDC_RANDOMIZATION_LIST_FILE attribute not set, using default."
            )
        )
        path = (os.path.join(settings.ETC_DIR, "randomization_list.csv"),)
    return path
