from __future__ import annotations

from typing import TYPE_CHECKING, Type

from django.apps import apps as django_apps
from django.conf import settings

from .default_definitions import default_definitions
from .facility import Facility, FacilityError

if TYPE_CHECKING:
    from .models import HealthFacility, Holiday


def get_holiday_model() -> str:
    return getattr(settings, "EDC_FACILITY_HOLIDAY_MODEL", "edc_facility.holiday")


def get_holiday_model_cls() -> Holiday:
    return django_apps.get_model(get_holiday_model())


def get_default_facility_name() -> str:
    return getattr(settings, "EDC_FACILITY_DEFAULT_FACILITY_NAME", "default")


def get_facility_definitions():
    return getattr(settings, "EDC_FACILITY_DEFINITIONS", default_definitions)


def get_facilities() -> dict[str, Facility]:
    """Returns a dictionary of facilities."""
    return {k: Facility(name=k, **v) for k, v in get_facility_definitions().items()}


def get_facility(name: str = None) -> Facility:
    """Returns a facility instance for this name, if it exists,
    or raises.
    """
    facilities = get_facilities()
    facility = facilities.get(name)
    if not facility:
        raise FacilityError(f"Facility '{name}' does not exist. Expected one of {facilities}.")
    return facility


def get_health_facility_model_cls() -> Type[HealthFacility]:
    return django_apps.get_model(get_health_facility_model())


def get_health_facility_model() -> str:
    return getattr(
        settings, "EDC_FACILITY_HEALTH_FACILITY_MODEL", "intecomm_facility.HealthFacility"
    )
