from django.apps import apps as django_apps
from django.conf import settings

from .model_mixins import (
    SUBJECT_VISIT_MISSED_REASONS_MODEL,
    SUBJECT_VISIT_MISSED_MODEL,
)


def get_subject_visit_model():
    return django_apps.get_model(settings.SUBJECT_VISIT_MODEL)


def get_subject_visit_missed_model():
    return django_apps.get_model(SUBJECT_VISIT_MISSED_MODEL)


def get_subject_visit_missed_reasons_model():
    return django_apps.get_model(SUBJECT_VISIT_MISSED_REASONS_MODEL)
