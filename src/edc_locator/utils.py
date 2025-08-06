from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.conf import settings

if TYPE_CHECKING:
    from .model_mixins import LocatorModelMixin


class LocatorModelError(Exception):
    pass


def get_locator_model() -> str:
    return getattr(settings, "SUBJECT_LOCATOR_MODEL", "edc_locator.subjectlocator")


def get_locator_model_cls() -> LocatorModelMixin:
    return django_apps.get_model(get_locator_model())
