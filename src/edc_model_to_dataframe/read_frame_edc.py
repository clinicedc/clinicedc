from django.apps import apps as django_apps
from django.db.models import QuerySet

from .model_to_dataframe import ModelToDataframe

__all__ = ["read_frame"]


def read_frame_edc(queryset: QuerySet | str = None, **kwargs):

    if not isinstance(queryset, QuerySet):
        queryset = django_apps.get_model(queryset).objects.all()
    m = ModelToDataframe(queryset=queryset, **kwargs)
    return m.dataframe
