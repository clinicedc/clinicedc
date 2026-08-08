import pandas as pd

from ..constants import date_datatypes


def normalize_date_columns(source_df: pd.DataFrame, columns: list[str] | None = None):
    columns = columns or source_df.select_dtypes(include="datetimetz").columns
    source_df[columns] = source_df[columns].apply(
        lambda x: x.dt.tz_convert("UTC").dt.normalize()
    )
    return source_df


def localize_date_columns(source_df: pd.DataFrame):
    columns = source_df.select_dtypes(include="datetimetz").columns
    source_df[columns] = source_df[columns].apply(
        lambda x: (
            x.dt.tz_convert("UTC").dt.tz_localize(None)
            if isinstance(x.dtype, pd.DatetimeTZDtype)
            else x
        )
    )
    return source_df


def get_model_fields_by_type(model_cls, fieldtype: str):
    cols = []
    for field_cls in model_cls._meta.get_fields():
        if field_cls.get_internal_type() == fieldtype:
            cols.append(field_cls.name)  # noqa: PERF401
    return cols


def get_date_model_fields(
    model_cls,
    source_df: pd.DataFrame | None,
) -> list[str]:
    source_cols = [] if source_df is None else source_df.columns
    date_cols = get_model_fields_by_type(model_cls, "DateField")
    return [col for col in date_cols if col in source_cols]


def get_datetime_model_fields(
    model_cls,
    source_df: pd.DataFrame | None,
) -> list[str]:
    source_cols = [] if source_df is None else source_df.columns
    date_cols = get_model_fields_by_type(model_cls, "DateTimeField")
    return [col for col in date_cols if col in source_cols]


def convert_dates_from_model(
    source_df: pd.DataFrame,
    model_cls,
    normalize: bool | None = None,
) -> pd.DataFrame:
    """Convert django date and datetime columns to pandas
    datetime64[us, UTC].
    """
    if date_cols := [
        *get_date_model_fields(model_cls, source_df),
        *get_datetime_model_fields(model_cls, source_df),
    ]:
        source_df[date_cols] = source_df[date_cols].apply(
            pd.to_datetime, errors="coerce", utc=True
        )
        if normalize:
            source_df = normalize_date_columns(source_df)
    return source_df
