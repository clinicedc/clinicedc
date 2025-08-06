import pandas as pd

from ..constants import timedelta_datatypes


def convert_timedelta_from_model(source_df: pd.DataFrame, model_cls) -> pd.DataFrame:
    date_cols = []
    for field_cls in model_cls._meta.get_fields():
        if field_cls.get_internal_type() in timedelta_datatypes:
            date_cols.append(field_cls.name)
    if date_cols:
        source_df[date_cols] = source_df[date_cols].apply(pd.to_timedelta, errors="coerce")
    return source_df
