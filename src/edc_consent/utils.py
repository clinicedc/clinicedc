from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from django import forms
from django.apps import apps as django_apps
from django.conf import settings
from django.db import models

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


def get_consent_model_cls() -> models.Model:
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
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    initials: Optional[str] = None,
    **kwargs,  # noqa
) -> None:
    if first_name and initials and last_name:
        try:
            if initials[:1] != first_name[:1] or initials[-1:] != last_name[:1]:
                raise InvalidInitials("Initials do not match full name.")
        except (IndexError, TypeError):
            raise InvalidInitials("Initials do not match full name.")


def values_as_string(*values) -> Optional[str]:
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
