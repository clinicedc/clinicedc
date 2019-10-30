from django.apps import apps as django_apps
from django.conf import settings

from .model_mixin import (
    RandomizationError,
    RandomizationListModelMixin,
    RandomizationListManager,
    RandomizationListModelError,
)
from .randomization_list import RandomizationList
import pdb


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
