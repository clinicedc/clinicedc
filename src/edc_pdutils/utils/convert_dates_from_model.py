import pandas as pd

from ..constants import date_datatypes


def convert_dates_from_model(
    source_df: pd.DataFrame,
    model_cls,
    normalize: bool | None = None,
    localize: bool | None = None,
) -> pd.DataFrame:
    """Convert django datetime columns to pandas datetime64 columns.

    Warning: When localizing, assumes stored values are tzinfo=UTC and only
    localizes dtypes datetime64[ns, UTC].
    """
    date_cols = []
    for field_cls in model_cls._meta.get_fields():
        if field_cls.get_internal_type() in date_datatypes:
            if field_cls.name in source_df.columns:
                date_cols.append(field_cls.name)
    if date_cols:
        source_df[date_cols] = source_df[date_cols].apply(pd.to_datetime, errors="coerce")
        if normalize:
            source_df[date_cols] = source_df[date_cols].apply(lambda x: x.dt.normalize())
        if localize:
            source_df[date_cols] = source_df[date_cols].apply(
                lambda x: (x.dt.tz_localize(None) if x.dtype == "datetime64[ns, UTC]" else x)
            )
    return source_df
