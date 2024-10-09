import pandas as pd

numeric_datatypes = [
    "DecimalField",
    "IntegerField",
    "BigIntegerField",
    "FloatField",
    "PositiveBigIntegerField",
    "PositiveIntegerField",
    "PositiveSmallIntegerField",
    "SmallIntegerField",
]

date_datatypes = ["DateTimeField", "DateField"]

timedelta_datatypes = ["DurationField"]


def convert_numerics_from_model(source_df: pd.DataFrame, model_cls) -> pd.DataFrame:
    numeric_cols = []
    for field_cls in model_cls._meta.get_fields():
        if field_cls.get_internal_type() in numeric_datatypes:
            numeric_cols.append(field_cls.name)
    if numeric_cols:
        source_df[numeric_cols] = source_df[numeric_cols].apply(pd.to_numeric, errors="coerce")
    return source_df


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
                lambda x: x.dt.tz_localize(None) if x.dtype == "datetime64[ns, UTC]" else x
            )
    return source_df


def convert_timedelta_from_model(source_df: pd.DataFrame, model_cls) -> pd.DataFrame:
    date_cols = []
    for field_cls in model_cls._meta.get_fields():
        if field_cls.get_internal_type() in timedelta_datatypes:
            date_cols.append(field_cls.name)
    if date_cols:
        source_df[date_cols] = source_df[date_cols].apply(pd.to_timedelta, errors="coerce")
    return source_df
