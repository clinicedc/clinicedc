from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.conf import settings
from django.utils.html import format_html

from .constants import ELIGIBLE, NOT_ELIGIBLE

if TYPE_CHECKING:
    from .model_mixins import ScreeningModelMixin


def get_subject_screening_app_label() -> str:
    return get_subject_screening_model().split(".")[0]


def get_subject_screening_model() -> str:
    return getattr(settings, "SUBJECT_SCREENING_MODEL")


def get_subject_screening_model_cls() -> ScreeningModelMixin:
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
