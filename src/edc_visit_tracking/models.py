from django.apps import apps as django_apps
from django.conf import settings
from edc_list_data.model_mixins import ListModelMixin

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


class SubjectVisitMissedReasons(ListModelMixin):
    class Meta(ListModelMixin.Meta):
        verbose_name = "Subject Missed Visit Reasons"
        verbose_name_plural = "Subject Missed Visit Reasons"
