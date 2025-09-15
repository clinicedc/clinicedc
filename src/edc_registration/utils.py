from __future__ import annotations

import re
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from edc_protocol.research_protocol_config import ResearchProtocolConfig

from .exceptions import RegisteredSubjectError

if TYPE_CHECKING:
    from edc_registration.models import RegisteredSubject


class RegisteredSubjectDoesNotExist(Exception):
    pass


def get_registered_subject_model_name() -> str:
    return getattr(
        settings,
        "EDC_REGISTRATION_REGISTERED_SUBJECT_MODEL",
        "edc_registration.registeredsubject",
    )


def get_registered_subject_model_cls() -> type[RegisteredSubject]:
    return django_apps.get_model(get_registered_subject_model_name())


def get_registered_subject(
    subject_identifier, raise_exception: bool | None = None, **kwargs
) -> RegisteredSubject | None:
    opts = dict(subject_identifier=subject_identifier, **kwargs)
    try:
        registered_subject = get_registered_subject_model_cls().objects.get(**opts)
    except ObjectDoesNotExist:
        registered_subject = None
    if raise_exception and not registered_subject:
        # the subject consent usually creates the registered subject
        # instance. Check the model is declared with
        # UpdatesOrCreatesRegistrationModelMixin
        raise RegisteredSubjectDoesNotExist(
            "Unknown subject. "
            f"Searched `{get_registered_subject_model_cls()._meta.label_lower}`. "
            f"Got {opts}."
        )
    return registered_subject


def valid_subject_identifier_or_raise(
    subject_identifier: str, raise_exception: bool | None = None
) -> bool:
    if not re.match(ResearchProtocolConfig().subject_identifier_pattern, subject_identifier):
        if raise_exception:
            raise RegisteredSubjectError(
                f"Invalid subject identifier format. "
                f"Valid pattern is `{ResearchProtocolConfig().subject_identifier_pattern}`. "
                f"See `edc_protocol.ResearchProtocolConfig().subject_identifier_pattern`. "
                f"Got `{subject_identifier}`."
            )
        return False
    return True
