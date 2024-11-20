import pandas as pd

from ..constants import numeric_datatypes


def convert_numerics_from_model(source_df: pd.DataFrame, model_cls) -> pd.DataFrame:
    numeric_cols = []
    for field_cls in model_cls._meta.get_fields():
        if field_cls.get_internal_type() in numeric_datatypes:
            numeric_cols.append(field_cls.name)
    if numeric_cols:
        source_df[numeric_cols] = source_df[numeric_cols].apply(pd.to_numeric, errors="coerce")
    return source_df
