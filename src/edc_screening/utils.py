from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from django import forms
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.urls import NoReverseMatch, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from edc_dashboard import url_names
from edc_dashboard.url_names import InvalidUrlName

from .constants import ELIGIBLE, NOT_ELIGIBLE
from .exceptions import InvalidScreeningIdentifierFormat

if TYPE_CHECKING:
    from .model_mixins import EligibilityModelMixin, ScreeningModelMixin


def get_subject_screening_app_label() -> str:
    return get_subject_screening_model().split(".")[0]


def get_subject_screening_model() -> str:
    return getattr(settings, "SUBJECT_SCREENING_MODEL")


def get_subject_screening_model_cls() -> Any:
    return django_apps.get_model(get_subject_screening_model())


def format_reasons_ineligible(*str_values: str, delimiter=None) -> str:
    reasons = None
    delimiter = delimiter or "|"
    str_values = tuple(x for x in str_values if x is not None)
    if str_values:
        reasons = format_html(delimiter.join(str_values))
    return reasons


def eligibility_display_label(eligible) -> str:
    return ELIGIBLE.upper() if eligible else NOT_ELIGIBLE


def validate_screening_identifier_format_or_raise(
    screening_identifier: str,
    pattern: str | None = None,
    exception_cls: Exception | None = None,
) -> None:
    """Validates the identifier pattern or raises."""
    pattern = pattern or r"^[A-Z0-9]+$"
    if not screening_identifier or not re.match(pattern, screening_identifier or ""):
        raise (exception_cls or InvalidScreeningIdentifierFormat)(
            f"Invalid screening identifier. Got `{screening_identifier}`."
        )


def get_subject_screening_or_raise(
    screening_identifier: str, is_modelform: bool | None = None
) -> ScreeningModelMixin:
    """Returns the subject_screening model instance or raises."""
    try:
        with transaction.atomic():
            subject_screening = get_subject_screening_model_cls().objects.get(
                screening_identifier=screening_identifier
            )
    except ObjectDoesNotExist as e:
        if is_modelform:
            raise forms.ValidationError("Not allowed. Screening form not found.")
        else:
            raise ObjectDoesNotExist(
                f"{e} screening_identifier={screening_identifier}. "
                "Perhaps catch this in the form."
            )
    return subject_screening


def is_eligible_or_raise(
    screening_identifier: str | None = None,
    subject_screening: EligibilityModelMixin | None = None,
    url_name: str | None = None,
) -> None:
    """Raise a ValidationError if subject_screening.eligible is False.

    * this func is NOT for the SubjectScreening form;
    * Adds a URl linking to the subject screening form in the validation message;
    * Default url name is `screening_listboard_url`.
    """
    if screening_identifier and subject_screening:
        raise TypeError(
            f"Expected one value not both. Got screening_identifier={screening_identifier} "
            f"and subject_screening={subject_screening}."
        )
    subject_screening = subject_screening or get_subject_screening_or_raise(
        screening_identifier, is_modelform=True
    )

    url_name = url_name or "screening_listboard_url"
    try:
        url_name = url_names.get(url_name)
    except InvalidUrlName:
        pass

    if not subject_screening.eligible:
        try:
            url = reverse(
                url_name,
                kwargs={"screening_identifier": subject_screening.screening_identifier},
            )
        except NoReverseMatch:
            try:
                url = reverse(url_name)
            except NoReverseMatch:
                url = None
            if url and url_name.endswith("changelist"):
                url = f"{url}?q={subject_screening.screening_identifier}"
        if not url:
            msg = format_html(
                "Not allowed. Subject is not eligible. "
                f"Got {subject_screening.screening_identifier}"
            )
        else:
            msg = format_html(
                'Not allowed. Subject is not eligible. See subject <A href="{}">{}</A>',
                mark_safe(url),  # nosec B308 B703
                subject_screening.screening_identifier,
            )
        raise forms.ValidationError(msg)
