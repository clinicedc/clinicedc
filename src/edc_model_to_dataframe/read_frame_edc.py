from __future__ import annotations

from django.apps import apps as django_apps
from django.db.models import QuerySet

from .model_to_dataframe import ModelToDataframe

__all__ = ["read_frame_edc"]


def read_frame_edc(
    model_or_queryset: QuerySet | str,
    *,
    drop_sys_columns: bool | None = None,
    drop_action_item_columns: bool | None = None,
    read_frame_verbose: bool | None = None,
):
    if not isinstance(model_or_queryset, QuerySet):
        qs = django_apps.get_model(model_or_queryset).objects.all()
    else:
        qs = model_or_queryset
    m = ModelToDataframe(
        queryset=qs,
        drop_sys_columns=drop_sys_columns,
        drop_action_item_columns=drop_action_item_columns,
        read_frame_verbose=read_frame_verbose,
    )
    if "site" not in m.dataframe.columns:
        m.dataframe["site"] = m.dataframe.site_id
    return m.dataframe
