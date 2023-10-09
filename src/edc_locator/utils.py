from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.conf import settings
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

if TYPE_CHECKING:
    from .model_mixins import LocatorModelMixin


class LocatorModelError(Exception):
    pass


def get_locator_model(visit_schedule_name: str | None = None) -> str:
    """Returns the locator model name in label_lower format.

    For now, cannot think of a case where more than one locator
    model would be required.
    Raises if visit_schedule declares a locator model != to
    SUBJECT_LOCATOR_MODEL.
    """
    locator_model = None
    if visit_schedule_name:
        visit_schedule = site_visit_schedules.get_visit_schedule(visit_schedule_name)
        locator_model = visit_schedule.locator_model
    if locator_model and locator_model != get_locator_model():
        raise LocatorModelError(
            f"Ambiguous Locator model. See settings.SUBJECT_LOCATOR_MODEL and "
            f"{visit_schedule_name}. Got `{settings.SUBJECT_LOCATOR_MODEL}` from "
            f"settings and `{locator_model}` from {visit_schedule_name}."
        )
    return getattr(settings, "SUBJECT_LOCATOR_MODEL", "edc_locator.subjectlocator")


def get_locator_model_cls(
    visit_schedule_name: str | None = None, locator_model: str | None = None
) -> LocatorModelMixin:
    """Returns the Locator model class.

    Uses visit_schedule_name to get the class from the visit schedule
    otherwise defaults to settings.SUBJECT_LOCATOR_MODEL.
    """
    locator_model = locator_model or get_locator_model(visit_schedule_name)
    return django_apps.get_model(locator_model)
