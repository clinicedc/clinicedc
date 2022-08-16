from typing import Optional, Type

from django.apps import apps as django_apps
from django.conf import settings
from django.db import models
from django.utils.html import format_html

from .constants import ELIGIBLE, NOT_ELIGIBLE


def get_subject_screening_app_label() -> Optional[str]:
    return get_subject_screening_model().split(".")[0]


def get_subject_screening_model() -> Optional[str]:
    return getattr(settings, "SUBJECT_SCREENING_MODEL", None)


def get_subject_screening_model_cls() -> Type[models.Model]:
    return django_apps.get_model(get_subject_screening_model())


def format_reasons_ineligible(*str_values: str, delimiter=None) -> str:
    reasons = None
    delimiter = delimiter or "|"
    str_values = tuple(x for x in str_values if x is not None)
    if str_values:
        reasons = format_html(delimiter.join(str_values))
    return reasons


def eligibility_display_label(eligible) -> str:
    return ELIGIBLE.upper() if eligible else NOT_ELIGIBLE
