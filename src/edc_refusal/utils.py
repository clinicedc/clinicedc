from django.apps import apps as django_apps
from django.conf import settings

from .model_mixins import SubjectRefusalModelMixin


def get_subject_refusal_model() -> str:
    return settings.SUBJECT_REFUSAL_MODEL


def get_subject_refusal_model_cls() -> SubjectRefusalModelMixin:
    return django_apps.get_model(get_subject_refusal_model())
