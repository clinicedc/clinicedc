from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable

from django import forms
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext as _
from edc_appointment.constants import INVALID_APPT_DATE
from edc_sites import site_sites
from edc_utils import formatted_datetime
from edc_utils.date import to_local

from .exceptions import (
    ConsentDefinitionDoesNotExist,
    NotConsentedError,
    SiteConsentError,
)
from .site_consents import site_consents

if TYPE_CHECKING:
    from edc_appointment.models import Appointment
    from edc_model.models import BaseUuidModel

    from edc_consent.consent_definition import ConsentDefinition

    from .model_mixins import ConsentModelMixin

    class ConsentModel(ConsentModelMixin, BaseUuidModel):
        ...


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
    appointment: Appointment = None,
    raise_validation_error: Callable = None,
) -> datetime:
    try:
        consent_definition = appointment.schedule.get_consent_definition(
            site=site_sites.get(appointment.site.id),
            report_datetime=report_datetime,
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

    consent_obj = get_consent_or_raise(
        model=appointment._meta.label_lower,
        subject_identifier=appointment.subject_identifier,
        report_datetime=report_datetime,
        consent_definition=consent_definition,
    )
    return consent_obj.consent_datetime


def get_consent_or_raise(
    model: str,
    subject_identifier: str,
    report_datetime: datetime,
    consent_definition: ConsentDefinition,
) -> ConsentModel:
    try:
        instance = consent_definition.model_cls.objects.get(
            subject_identifier=subject_identifier,
            consent_datetime__lte=report_datetime,
            version=consent_definition.version,
        )
    except ObjectDoesNotExist:
        date_string = formatted_datetime(to_local(report_datetime))
        raise NotConsentedError(
            f"Consent is required. Could not find a valid consent when saving model "
            f"'{model}' for subject '{subject_identifier}' using "
            f"date '{date_string}'. On which date was the subject consented? "
            f"See consent definition `{consent_definition.display_name}`."
        )
    return instance
