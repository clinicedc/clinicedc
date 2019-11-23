import os
import sys

from django.apps import apps as django_apps
from django.conf import settings
from django.core.management.color import color_style

from .constants import ACTIVE, PLACEBO

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
    return settings.EDC_RANDOMIZATION_LIST_FILE


def get_assignment_map():
    return getattr(
        settings, "EDC_RANDOMIZATION_ASSIGNMENT_MAP", {ACTIVE: 1, PLACEBO: 2}
    )
