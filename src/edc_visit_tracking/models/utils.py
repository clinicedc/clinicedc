from typing import Type

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models

from ..stubs import TSubjectVisitModelStub


def get_subject_visit_model_cls() -> TSubjectVisitModelStub:
    return django_apps.get_model(settings.SUBJECT_VISIT_MODEL)


def get_subject_visit_missed_reasons_model() -> Type[models.Model]:
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


def get_subject_visit_missed_model() -> Type[models.Model]:
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
    return django_apps.get_model(model)
