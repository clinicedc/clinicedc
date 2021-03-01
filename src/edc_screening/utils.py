from typing import Optional, Type

from django.apps import apps as django_apps
from django.conf import settings
from django.db import models
from django.utils.html import format_html
from edc_constants.constants import NO, NORMAL, YES


def if_yes(value) -> bool:
    """Returns True if value is YES."""
    if value == NORMAL:
        return True
    return value == YES


def if_no(value) -> bool:
    """Returns True if value is NO."""
    return value == NO


def if_normal(value) -> bool:
    """Returns True if value is NORMAL."""
    return value == NORMAL


def get_subject_screening_model_name() -> Optional[str]:
    return getattr(settings, "SUBJECT_SCREENING_MODEL", None)


def get_subject_screening_model_cls() -> Type[models.Model]:
    return django_apps.get_model(get_subject_screening_model_name())


def get_subject_screening(
    subject_screening_model: str, screening_identifier: str
) -> models.Model:
    """Returns the subject screening model instance or raises"""
    model_cls = django_apps.get_model(subject_screening_model)
    return model_cls.objects.get(screening_identifier=screening_identifier)


def format_reasons_ineligible(*str_values: str, delimiter=None) -> str:
    reasons = None
    delimiter = delimiter or "|"
    str_values = tuple(x for x in str_values if x is not None)
    if str_values:
        reasons = "".join(str_values)
        reasons = format_html(reasons.replace(delimiter, "<BR>"))
    return reasons


def eligibility_display_label(eligible) -> str:
    return "ELIGIBLE" if eligible else "not eligible"
