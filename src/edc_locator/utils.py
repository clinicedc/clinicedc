from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.conf import settings
from edc_visit_schedule import site_visit_schedules

if TYPE_CHECKING:
    from .model_mixins import LocatorModelMixin


class LoctorModelError(Exception):
    pass


def get_locator_model(visit_schedule_name: str | None = None) -> str:
    """Returns the locator model name in label_lower format"""
    if visit_schedule_name:
        visit_schedule = site_visit_schedules.get_visit_schedule(visit_schedule_name)
        return visit_schedule.locator_model
    return getattr(settings, "EDC_LOCATOR_LOCATOR_MODEL", "edc_locator.subjectlocator")


def get_locator_model_cls(
    visit_schedule_name: str | None = None, locator_model: str | None = None
) -> LocatorModelMixin:
    """Returns the Locator model class.

    Uses visit_schedule_name to get the class from the visit schedule
    otherwise defaults to settings.EDC_LOCATOR_LOCATOR_MODEL.
    """
    locator_model = locator_model or get_locator_model(visit_schedule_name)
    return django_apps.get_model(locator_model)
