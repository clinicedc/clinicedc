from __future__ import annotations

import pandas as pd
from django.apps import apps as django_apps
from django.db.models import QuerySet

from .model_to_dataframe import ModelToDataframe

__all__ = ["read_frame_edc"]


def read_frame_edc(
        model_or_queryset: QuerySet | str,
        *,
        drop_sys_columns: bool | None = None,
        drop_action_item_columns: bool | None = None,
        convert_visit_code_to_float: bool | None = None,
        read_frame_verbose: bool | None = None,
):
    if not isinstance(model_or_queryset, QuerySet):
        qs: QuerySet = django_apps.get_model(model_or_queryset).objects.all()
    else:
        qs: QuerySet = model_or_queryset
    m = ModelToDataframe(
        queryset=qs,
        drop_sys_columns=drop_sys_columns,
        drop_action_item_columns=drop_action_item_columns,
        read_frame_verbose=read_frame_verbose,
        convert_visit_code_to_float=convert_visit_code_to_float,
    )
    if "site" not in m.dataframe.columns:
        m.dataframe["site"] = m.dataframe["site_id"].astype("string")
    m.dataframe.convert_dtypes()
    for column in m.dataframe.select_dtypes(include="string").columns:
        m.dataframe[column] = m.dataframe[column].astype(pd.StringDtype(na_value=pd.NA))
    return m.dataframe.reset_index(drop=True)
