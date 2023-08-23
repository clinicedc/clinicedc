from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django import forms
from django.apps import apps as django_apps
from django.conf import settings
from django.db import models
from edc_sites.get_countries import get_countries

from edc_consent import site_consents
from edc_consent.site_consents import SiteConsentError

if TYPE_CHECKING:
    from edc_consent.consent import Consent


class InvalidInitials(Exception):
    pass


class MinimumConsentAgeError(Exception):
    pass


def get_consent_model_name() -> str:
    return settings.SUBJECT_CONSENT_MODEL


def get_consent_model_cls() -> Any:
    return django_apps.get_model(get_consent_model_name())


def get_consent_for_period_or_raise(report_datetime) -> Consent:
    try:
        consent_object = site_consents.get_consent_for_period(
            model=get_consent_model_name(),
            report_datetime=report_datetime,
            consent_group=get_default_consent_group(),
        )
    except SiteConsentError as e:
        raise forms.ValidationError(e)
    return consent_object


def get_reconsent_model_name() -> str:
    return getattr(
        settings,
        "SUBJECT_RECONSENT_MODEL",
        f"{get_consent_model_name().split('.')[0]}.subjectreconsent",
    )


def get_reconsent_model_cls() -> models.Model:
    return django_apps.get_model(get_reconsent_model_name())


def get_default_consent_group() -> str:
    return django_apps.get_app_config("edc_consent").default_consent_group


def verify_initials_against_full_name(
    first_name: str | None = None,
    last_name: str | None = None,
    initials: str | None = None,
    **kwargs,  # noqa
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


def get_site_ids_with_pii_perms(all_sites) -> list[int]:
    site_ids = []
    countries_with_pii_perms = [
        c for c in get_countries() if c not in get_remove_patient_names_from_countries()
    ]
    for country in countries_with_pii_perms:
        site_ids.extend([s.site_id for s in all_sites.get(country)])
    return site_ids
