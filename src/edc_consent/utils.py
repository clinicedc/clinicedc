from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable

from django import forms
from django.apps import apps as django_apps
from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _
from edc_appointment.constants import INVALID_APPT_DATE
from edc_registration import get_registered_subject_model_cls
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from . import ConsentDefinitionDoesNotExist
from .exceptions import NotConsentedError
from .requires_consent import RequiresConsent
from .site_consents import SiteConsentError, site_consents

if TYPE_CHECKING:
    from edc_consent.consent_definition import ConsentDefinition


class InvalidInitials(Exception):
    pass


class MinimumConsentAgeError(Exception):
    pass


def get_consent_model_name() -> str:
    return settings.SUBJECT_CONSENT_MODEL


def get_consent_model_cls() -> Any:
    return django_apps.get_model(get_consent_model_name())


def get_consent_for_period_or_raise(report_datetime) -> ConsentDefinition:
    try:
        consent_definition = site_consents.get_consent_definition(
            model=get_consent_model_name(),
            report_datetime=report_datetime,
        )
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


def consent_datetime_or_raise(
    report_datetime: datetime = None,
    model_obj=None,
    raise_validation_error: Callable = None,
) -> datetime:
    model_cls = site_visit_schedules.get_consent_model(
        visit_schedule_name=model_obj.visit_schedule_name,
        schedule_name=model_obj.schedule_name,
    )
    try:
        RequiresConsent(
            model=model_obj._meta.label_lower,
            subject_identifier=model_obj.subject_identifier,
            report_datetime=report_datetime,
            consent_model=model_cls,
        )
    except SiteConsentError:
        if raise_validation_error:
            possible_consents = "', '".join(
                [cdef.display_name for cdef in site_consents.consent_definitions]
            )
            raise_validation_error(
                {
                    "appt_datetime": _(
                        "Date does not fall within a valid consent period. "
                        "Possible consents are '%(possible_consents)s'. "
                        % {"possible_consents": possible_consents}
                    )
                },
                INVALID_APPT_DATE,
            )
        else:
            raise
    except NotConsentedError as e:
        if raise_validation_error:
            raise_validation_error(
                {"appt_datetime": str(e)},
                INVALID_APPT_DATE,
            )
        else:
            raise
    registered_subject = get_registered_subject_model_cls().objects.get(
        subject_identifier=model_obj.subject_identifier
    )
    return registered_subject.consent_datetime
