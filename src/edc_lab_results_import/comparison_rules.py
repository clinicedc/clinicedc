"""The rule that decides whether an imported result agrees with the
result CRF.

This is the single implementation. `ResultComparison` applies it to the
handful of rows behind one CRF on the result search page, and
`get_df_result_comparison` applies it to every result CRF in the trial.
Both call `add_comparison_columns`, so the page and the dataframe can
never disagree about the same row.

Value, units and the abnormal flag are compared separately, so a row
that agrees on the value but not on the units still reads as a
difference.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from clinicedc_constants import NO, YES

from .constants import ABNORMAL_FLAGS, DIFFERS, MATCH, NOT_COMPARED

__all__ = [
    "COMPARISON_COLUMNS",
    "RULE_COLUMNS",
    "add_comparison_columns",
    "as_bool",
    "get_abnormal",
    "quantize",
]

# columns `add_comparison_columns` reads
RULE_COLUMNS = (
    "has_import",
    "crf_value",
    "crf_units",
    "crf_abnormal",
    "decimal_places",
    "result_value",
    "units",
    "converted_result_value",
    "converted_units",
    "flag",
)

# columns `add_comparison_columns` writes
COMPARISON_COLUMNS = (
    "abnormal",
    "comparable_value",
    "value_status",
    "units_status",
    "abnormal_status",
    "abs_diff",
    "pct_diff",
    "ratio",
)


def as_bool(condition: pd.Series) -> np.ndarray:
    """Return `condition` as a plain numpy bool array.

    Comparing two nullable dtypes gives a `boolean` series, and NA in
    one of those is ambiguous to `np.where` and `np.select`. NA is not
    a match, so it becomes False.
    """
    return condition.fillna(False).to_numpy(dtype=bool)


def quantize(values: pd.Series, decimal_places: pd.Series) -> pd.Series:
    """Return `values` rounded half away from zero to `decimal_places`.

    This is `decimal.ROUND_HALF_UP`, which numpy does not offer:
    `np.round` rounds half to even. Values are float64, so the scaled
    value of an exact half can land just below the boundary, for example
    2.675 * 100 is 267.49999999999997. The relative epsilon pulls those
    back over it, and is far smaller than any difference the source
    data can express.

    Values are returned unrounded where `decimal_places` is null, which
    is the case for a value field that is not a `DecimalField`.
    """
    values = pd.to_numeric(values, errors="coerce").astype("float64")
    places = pd.to_numeric(decimal_places, errors="coerce").astype("float64")
    factor = np.power(10.0, places)
    scaled = values.abs() * factor
    rounded = np.sign(values) * np.floor(scaled + 0.5 + scaled * 1e-12) / factor
    return rounded.where(places.notna(), values)


def get_abnormal(flag: pd.Series, has_import: pd.Series) -> pd.Series:
    """Return the abnormal flag implied by the lab's `flag`.

    A blank flag means the lab did not call the value abnormal. A flag
    that is neither blank nor recognized is not interpreted, and is
    returned as an empty string. A row with no imported result has no
    flag to read, and is returned as NA.
    """
    flag = flag.astype("string").fillna("").str.strip().str.lower()
    abnormal = pd.Series(
        np.where(
            as_bool(flag == ""),
            NO,
            np.where(as_bool(flag.isin(ABNORMAL_FLAGS)), YES, ""),
        ),
        index=flag.index,
        dtype="string",
    )
    return abnormal.where(has_import, pd.NA)


def get_comparable_value(df: pd.DataFrame) -> pd.Series:
    """Return the imported value in the units used by the CRF.

    Returns NA where the two cannot be expressed in the same units, in
    which case the value is not compared. The units difference is
    reported on its own.
    """
    units = df["units"].astype("string").fillna("")
    converted_units = df["converted_units"].astype("string").fillna("")
    crf_units = df["crf_units"].astype("string").fillna("")
    value = pd.to_numeric(df["result_value"], errors="coerce").astype("float64")
    converted_value = pd.to_numeric(df["converted_result_value"], errors="coerce").astype(
        "float64"
    )
    comparable = pd.Series(np.nan, index=df.index, dtype="float64")
    comparable = comparable.mask(as_bool((units != "") & (units == crf_units)), value)
    return comparable.mask(
        as_bool(comparable.isna() & (converted_units != "") & (converted_units == crf_units)),
        converted_value,
    )


def get_value_status(df: pd.DataFrame, rounded_imported: pd.Series, rounded_crf: pd.Series):
    """Return MATCH, DIFFERS or NOT_COMPARED for the value.

    Two blank values agree. One blank value does not. A value that
    cannot be expressed in the CRF's units is not compared. Otherwise
    the two are compared at the precision the CRF stores, so 13.4000
    and 13.4 do not read as a difference.
    """
    crf_value = pd.to_numeric(df["crf_value"], errors="coerce")
    result_value = pd.to_numeric(df["result_value"], errors="coerce")
    both_blank = crf_value.isna() & result_value.isna()
    either_blank = crf_value.isna() | result_value.isna()
    return pd.Series(
        np.select(
            [
                as_bool(~df["has_import"]),
                as_bool(both_blank),
                as_bool(either_blank),
                as_bool(df["comparable_value"].isna()),
                as_bool(rounded_imported == rounded_crf),
            ],
            [NOT_COMPARED, MATCH, DIFFERS, NOT_COMPARED, MATCH],
            default=DIFFERS,
        ),
        index=df.index,
        dtype="string",
    )


def add_comparison_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Return `df` with the comparison and difference columns added.

    `df` must carry `RULE_COLUMNS`. See `RULE_COLUMNS` and
    `COMPARISON_COLUMNS`.
    """
    if missing := [col for col in RULE_COLUMNS if col not in df.columns]:
        raise KeyError(f"Missing column(s) required to compare results. Got {missing}.")
    df = df.copy()
    df["has_import"] = df["has_import"].astype("boolean").fillna(False).astype(bool)
    df["abnormal"] = get_abnormal(df["flag"], df["has_import"])
    df["comparable_value"] = get_comparable_value(df)

    rounded_imported = quantize(df["comparable_value"], df["decimal_places"])
    rounded_crf = quantize(df["crf_value"], df["decimal_places"])

    df["value_status"] = get_value_status(df, rounded_imported, rounded_crf)
    df["units_status"] = pd.Series(
        np.where(
            as_bool(~df["has_import"]),
            NOT_COMPARED,
            np.where(
                as_bool(
                    df["units"].astype("string").fillna("")
                    == df["crf_units"].astype("string").fillna("")
                ),
                MATCH,
                DIFFERS,
            ),
        ),
        index=df.index,
        dtype="string",
    )
    df["abnormal_status"] = pd.Series(
        np.where(
            as_bool(df["abnormal"].isna() | (df["abnormal"] == "")),
            NOT_COMPARED,
            np.where(
                as_bool(df["abnormal"] == df["crf_abnormal"].astype("string").fillna("")),
                MATCH,
                DIFFERS,
            ),
        ),
        index=df.index,
        dtype="string",
    )

    # differences are taken at the CRF's precision, so a value that
    # differs only in the decimal places the CRF does not store reads
    # as exactly 0.0 and sorts to the bottom
    df["abs_diff"] = (rounded_imported - rounded_crf).abs()
    # the lab result is the source of truth, the CRF is the
    # transcription being checked, so the imported value is the
    # denominator. A zero or missing denominator gives NaN, which sorts
    # out of the way rather than to the top
    df["pct_diff"] = 100.0 * df["abs_diff"] / rounded_imported.abs().replace(0.0, np.nan)
    # a ratio at or near a power of ten is a decimal point slip, which
    # a percentage difference buries among the large differences
    df["ratio"] = rounded_imported / rounded_crf.replace(0.0, np.nan)
    return df
