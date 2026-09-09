from __future__ import annotations

import pandas as pd
from clinicedc_constants import NO
from django.apps import apps as django_apps
from django.conf import settings
from django_pandas.io import read_frame

from edc_lab_results.dataframes import get_df_result_crfs

from ..comparison_rules import add_comparison_columns
from ..models import Result
from ..utils import get_requisition_panel_name_map
from .staleness import stamp_pulled_datetime

__all__ = ["get_df_result_comparison"]

REQUISITION_KEY = ("requisition_id", "utestid")
SUBJECT_VISIT_KEY = ("subject_visit_id", "panel_name", "utestid")

IMPORTED_COLUMNS = (
    "result_id",
    "result_value",
    "units",
    "converted_result_value",
    "converted_units",
    "flag",
    "result_datetime",
    "source_file",
    "requisition_identifier",
)

COMPARISON_FRAME_COLUMNS = (
    # identity
    "subject_identifier",
    "visit_code",
    "visit_code_sequence",
    "visit_datetime",
    "panel_name",
    "crf_model",
    "crf_id",
    "subject_visit_id",
    "requisition_id",
    "requisition_identifier",
    "utestid",
    # CRF
    "crf_value",
    "crf_units",
    "crf_abnormal",
    "decimal_places",
    # imported
    "result_value",
    "units",
    "converted_result_value",
    "converted_units",
    "flag",
    "abnormal",
    "result_datetime",
    "source_file",
    "result_id",
    # join
    "join_key",
    "n_imported_for_key",
    "panel_imported",
    # the requisition's own account of whether a result was coming
    "result_expected",
    "result_not_expected_reason",
    "result_expected_conflict",
    # comparison
    "comparable_value",
    "value_status",
    "units_status",
    "abnormal_status",
    "abs_diff",
    "pct_diff",
    "ratio",
)


def get_df_result_comparison() -> pd.DataFrame:
    """Return a trial-wide dataframe reconciling every result CRF value
    against the imported lab results.

    One row per result CRF instance per utest id, whether or not the
    value was keyed and whether or not a result was imported for it, so
    every CRF value that does not compare is listed with the reason
    readable from its status columns. Imported utest ids with no field
    on the CRF are left out, as are imported results with no CRF, which
    the result search page already surfaces as an add button.

    Rows are joined on requisition and utest id, falling back to
    related visit, panel and utest id for the baseline results that
    carry no requisition. `join_key` says which matched.

    Every imported result matching a key is kept rather than collapsed,
    so a corrected report filed against the same requisition as the
    original, and repeat testing at one requisition, both show as more
    than one row. `n_imported_for_key` counts them, and is 0 where
    nothing was imported for that key.

    `panel_imported` separates a CRF whose panel was never imported at
    all, meaning a missing source document, from one whose panel was
    imported but is missing this utest id, meaning a mapping gap. See
    `get_mappings`.

    Values and differences are float64. Differences are taken at the
    precision the CRF stores, so a value differing only in decimal
    places the CRF does not hold reads as exactly 0.0. See
    `comparison_rules`, which the result search page shares.
    """
    df_crf = get_df_result_crfs()
    if df_crf.empty:
        return stamp_pulled_datetime(pd.DataFrame(columns=list(COMPARISON_FRAME_COLUMNS)))
    df_imported = get_df_imported()
    df = merge_imported(df_crf, df_imported)
    df["panel_imported"] = get_panel_imported(df, df_imported)
    df["has_import"] = df["n_imported_for_key"] > 0
    df = add_comparison_columns(df)
    df = df.merge(get_df_result_expected(), on=["subject_visit_id", "panel_name"], how="left")
    # the requisition says the lab will never report, yet results were
    # imported against it. Someone has to look at these
    df["result_expected_conflict"] = (
        (df["result_expected"] == NO) & (df["n_imported_for_key"] > 0)
    ).fillna(False)
    df = (
        df.reindex(columns=list(COMPARISON_FRAME_COLUMNS))
        .sort_values(["subject_identifier", "visit_code", "panel_name", "utestid"])
        .reset_index(drop=True)
    )
    return stamp_pulled_datetime(df)


def get_df_result_expected() -> pd.DataFrame:
    """Return each requisition's account of whether a result is coming.

    Keyed by related visit and panel, which
    `RequisitionModelMixin.Meta` constrains to be unique together, so
    this reaches a CRF whose own requisition field is empty. A CRF value
    with no imported result and `result_expected` of NO is an explained
    absence, not a gap.
    """
    model_cls = django_apps.get_model(settings.SUBJECT_REQUISITION_MODEL)
    visit_attr = model_cls.related_visit_model_attr()
    df = read_frame(
        model_cls.objects.values(
            visit_attr, "panel__name", "result_expected", "result_not_expected_reason"
        ).all(),
        verbose=False,
    ).rename(columns={visit_attr: "subject_visit_id", "panel__name": "panel_name"})
    if df.empty:
        return pd.DataFrame(
            columns=[
                "subject_visit_id",
                "panel_name",
                "result_expected",
                "result_not_expected_reason",
            ]
        )
    for col in ["subject_visit_id", "panel_name"]:
        df[col] = df[col].astype("string").str.strip().replace("", pd.NA)
    for col in ["result_expected", "result_not_expected_reason"]:
        df[col] = df[col].astype("string")
    return df.reset_index(drop=True)


def get_df_imported() -> pd.DataFrame:
    """Return the imported results, one row per result."""
    df = read_frame(
        Result.objects.values(
            "id",
            "subject_visit",
            "requisition",
            "requisition_identifier",
            "panel_name",
            "utestid",
            "result_value",
            "units",
            "converted_result_value",
            "converted_units",
            "flag",
            "result_datetime",
            "source_file",
        ).all(),
        verbose=False,
    ).rename(
        columns={
            "id": "result_id",
            "subject_visit": "subject_visit_id",
            "requisition": "requisition_id",
        }
    )
    if df.empty:
        return pd.DataFrame(
            columns=[
                "subject_visit_id",
                "requisition_id",
                "panel_name",
                "utestid",
                *IMPORTED_COLUMNS,
            ]
        )
    for col in ["result_id", "subject_visit_id", "requisition_id", "panel_name", "utestid"]:
        df[col] = df[col].astype("string").str.strip().replace("", pd.NA)
    for col in ["result_value", "converted_result_value"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")
    for col in ["units", "converted_units", "flag", "source_file", "requisition_identifier"]:
        df[col] = df[col].astype("string").fillna("")
    # the CRF grid is keyed by the panel the specimen was drawn under,
    # so the imported side has to agree. A differential result reports
    # `wbc_diff` but is collected on the FBC requisition. See
    # `get_requisition_panel_name_map`
    df["panel_name"] = df["panel_name"].replace(get_requisition_panel_name_map())
    return df.reset_index(drop=True)


def merge_imported(df_crf: pd.DataFrame, df_imported: pd.DataFrame) -> pd.DataFrame:
    """Return the CRF grid with the imported results joined onto it.

    The requisition key is tried first, then the related visit key for
    whatever it left unmatched, which covers both a CRF with no
    requisition and a CRF whose requisition was never carried onto the
    imported result.
    """
    df_crf = df_crf.reset_index(drop=True)
    df_crf["_row"] = df_crf.index
    frames = []
    unmatched = df_crf
    for join_key, key in [
        ("requisition", list(REQUISITION_KEY)),
        ("subject_visit", list(SUBJECT_VISIT_KEY)),
    ]:
        left = unmatched[unmatched[key].notna().all(axis=1)]
        right = df_imported.dropna(subset=key)
        if left.empty or right.empty:
            continue
        counts = (
            right.groupby(key, dropna=False).size().rename("n_imported_for_key").reset_index()
        )
        merged = left.merge(
            right[[*key, *IMPORTED_COLUMNS]].merge(counts, on=key, how="left"),
            on=key,
            how="inner",
        )
        if merged.empty:
            continue
        merged["join_key"] = join_key
        frames.append(merged)
        unmatched = unmatched[~unmatched["_row"].isin(merged["_row"])]
    frames.append(unmatched.assign(join_key=pd.NA, n_imported_for_key=0))
    df = pd.concat(frames, ignore_index=True)
    # a frame of rows that matched nothing carries no imported columns
    for col in IMPORTED_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA
    df["join_key"] = df["join_key"].astype("string")
    df["n_imported_for_key"] = df["n_imported_for_key"].fillna(0).astype("Int64")
    return df.drop(columns=["_row"])


def get_panel_imported(df: pd.DataFrame, df_imported: pd.DataFrame) -> pd.Series:
    """Return whether anything at all was imported for each row's panel.

    False means no source document reached this requisition or
    timepoint. True with `n_imported_for_key` of 0 means the panel was
    imported but this utest id was not among the results.
    """
    requisition_ids = set(df_imported["requisition_id"].dropna())
    visit_panels = set(
        df_imported.dropna(subset=["subject_visit_id", "panel_name"])
        .loc[:, ["subject_visit_id", "panel_name"]]
        .itertuples(index=False, name=None)
    )
    by_requisition = df["requisition_id"].isin(requisition_ids)
    by_visit_panel = pd.Series(
        list(zip(df["subject_visit_id"], df["panel_name"], strict=True)), index=df.index
    ).isin(visit_panels)
    return by_requisition | by_visit_panel
