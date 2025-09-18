from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from django import forms
from django.apps import apps as django_apps
from django.conf import settings
from django.db import models

from edc_sites import site_sites

from .exceptions import ConsentDefinitionDoesNotExist
from .site_consents import site_consents

if TYPE_CHECKING:
    from edc_consent.consent_definition import ConsentDefinition
    from edc_model.models import BaseUuidModel

    from .model_mixins import ConsentModelMixin

    class ConsentModel(ConsentModelMixin, BaseUuidModel): ...


class InvalidInitials(Exception):
    pass


class MinimumConsentAgeError(Exception):
    pass


def get_consent_model_name() -> str:
    return settings.SUBJECT_CONSENT_MODEL


def get_consent_model_cls() -> Any:
    return django_apps.get_model(get_consent_model_name())


def get_consent_definition_or_raise(
    model: str | None = None,
    report_datetime: datetime | None = None,
    site_id: int | None = None,
    version: int | None = None,
) -> ConsentDefinition:
    opts = {}
    if model:
        opts.update(model=model)
    if report_datetime:
        opts.update(report_datetime=report_datetime)
    if version:
        opts.update(version=version)
    if site_id:
        opts.update(site=site_sites.get(site_id))
    try:
        consent_definition = site_consents.get_consent_definition(**opts)
    except ConsentDefinitionDoesNotExist as e:
        raise forms.ValidationError(e)
    return consent_definition


def get_reconsent_model_name() -> str:
    return getattr(
        settings,
        "SUBJECT_RECONSENT_MODEL",
        f"{get_consent_model_name().split('.')[0]}.subjectreconsent",
    )


def get_reconsent_model_cls() -> models.Model:
    return django_apps.get_model(get_reconsent_model_name())


def verify_initials_against_full_name(
    first_name: str | None = None,
    last_name: str | None = None,
    initials: str | None = None,
    **kwargs,
) -> None:
    if first_name and initials and last_name:
        try:
            if initials[:1] != first_name[:1] or initials[-1:] != last_name[:1]:
                raise InvalidInitials("Initials do not match full name.")
        except (IndexError, TypeError):
            raise InvalidInitials("Initials do not match full name.")


def values_as_string(*values) -> str | None:
    if not any([True for v in values if v is None]):
        as_string = ""
        for value in values:
            try:
                value = value.isoformat()
            except AttributeError:
                pass
            as_string = f"{as_string}{value}"
        return as_string
    return None


def get_remove_patient_names_from_countries() -> list[str]:
    """Returns a list of country names."""
    return getattr(settings, "EDC_CONSENT_REMOVE_PATIENT_NAMES_FROM_COUNTRIES", [])
