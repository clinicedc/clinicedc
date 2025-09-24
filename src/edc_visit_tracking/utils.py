from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, TypeVar

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .exceptions import RelatedVisitModelError

if TYPE_CHECKING:
    from edc_list_data.model_mixins import ListModelMixin

    from .models import SubjectVisit, SubjectVisitMissed

    ListModel = TypeVar("ListModel", bound=ListModelMixin)


def get_related_visit_model() -> str:
    """Returns the label_lower of the related visit model for this
    project.

    One `related visit model` allowed per project.
    """
    return getattr(settings, "SUBJECT_VISIT_MODEL", "edc_visit_tracking.subjectvisit")


def get_related_visit_model_cls() -> type[SubjectVisit]:
    model_cls = django_apps.get_model(get_related_visit_model())
    if model_cls._meta.proxy:
        # raise for now until we have a solution
        raise RelatedVisitModelError(
            f"Not allowed. Related visit model may not be a proxy model. Got {model_cls}. "
        )
    return model_cls


def get_subject_visit_model() -> str:
    warnings.warn(
        "This func has been renamed to `get_related_visit_model`.",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_related_visit_model()


def get_subject_visit_model_cls() -> type[SubjectVisit]:
    warnings.warn(
        "This func has been renamed to `get_related_visit_model_cls`.",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_related_visit_model_cls()


def get_subject_visit_missed_model() -> str:
    error_msg = (
        "Settings attribute `SUBJECT_VISIT_MISSED_MODEL` not set. Update settings. "
        "For example, `SUBJECT_VISIT_MISSED_MODEL=meta_subject.subjectvisitmissed`. "
        "See also `SubjectVisitMissedModelMixin`."
    )
    try:
        model = settings.SUBJECT_VISIT_MISSED_MODEL
    except AttributeError as e:
        raise ImproperlyConfigured(f"{error_msg} Got {e}.") from e
    else:
        if not model:
            raise ImproperlyConfigured(f"{error_msg} Got None.")
    return model


def get_allow_missed_unscheduled_appts() -> bool:
    """Returns value of settings attr or False"""
    return getattr(settings, "EDC_VISIT_TRACKING_ALLOW_MISSED_UNSCHEDULED", False)


def get_subject_visit_missed_model_cls() -> type[SubjectVisitMissed]:
    return django_apps.get_model(get_subject_visit_missed_model())


def get_previous_related_visit(
    related_visit: SubjectVisit, include_interim=None
) -> SubjectVisit | None:
    if related_visit:
        if include_interim:
            previous_appointment = related_visit.appointment.relative_previous
        else:
            previous_appointment = related_visit.appointment.previous
        return getattr(previous_appointment, "related_visit", None)
    return None


def get_next_related_visit(
    related_visit: SubjectVisit, include_interim=None
) -> SubjectVisit | None:
    if related_visit:
        if include_interim:
            next_appointment = related_visit.appointment.relative_next
        else:
            next_appointment = related_visit.appointment.next
        return getattr(next_appointment, "related_visit", None)
    return None
