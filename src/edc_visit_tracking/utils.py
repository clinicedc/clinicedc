from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

if TYPE_CHECKING:
    from edc_list_data.model_mixins import ListModelMixin

    from .model_mixins import SubjectVisitMissedModelMixin, VisitModelMixin

    VisitModel = TypeVar("VisitModel", bound=VisitModelMixin)
    VisitMissedModel = TypeVar("VisitMissedModel", bound=SubjectVisitMissedModelMixin)
    ListModel = TypeVar("ListModel", bound=ListModelMixin)


def get_related_visit_model() -> str:
    return settings.SUBJECT_VISIT_MODEL


def get_related_visit_model_cls() -> VisitModel:
    return django_apps.get_model(settings.SUBJECT_VISIT_MODEL)


def get_subject_visit_model() -> str:
    return get_related_visit_model()


def get_subject_visit_model_cls() -> VisitModel:
    return get_related_visit_model_cls()


def get_subject_visit_missed_reasons_model() -> ListModel:
    error_msg = (
        "Settings attribute `SUBJECT_VISIT_MISSED_REASONS_MODEL` not set. "
        "Update settings. For example, `SUBJECT_VISIT_MISSED_REASONS_MODEL"
        "=meta_lists.subjectvisitmissedreasons`. "
        "See also `SubjectVisitMissedModelMixin`."
    )
    try:
        model = settings.SUBJECT_VISIT_MISSED_REASONS_MODEL
    except AttributeError as e:
        raise ImproperlyConfigured(f"{error_msg} Got {e}.")
    else:
        if not model:
            raise ImproperlyConfigured(f"{error_msg} Got None.")
    return model


def get_subject_visit_missed_model() -> str:
    error_msg = (
        "Settings attribute `SUBJECT_VISIT_MISSED_MODEL` not set. Update settings. "
        "For example, `SUBJECT_VISIT_MISSED_MODEL=meta_subject.subjectvisitmissed`. "
        "See also `SubjectVisitMissedModelMixin`."
    )
    try:
        model = settings.SUBJECT_VISIT_MISSED_MODEL
    except AttributeError as e:
        raise ImproperlyConfigured(f"{error_msg} Got {e}.")
    else:
        if not model:
            raise ImproperlyConfigured(f"{error_msg} Got None.")
    return model


def get_subject_visit_missed_model_cls() -> VisitMissedModel:
    return django_apps.get_model(get_subject_visit_missed_model())
