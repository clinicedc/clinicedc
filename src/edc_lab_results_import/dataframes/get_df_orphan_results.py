from __future__ import annotations

import numpy as np
import pandas as pd
from django.apps import apps as django_apps
from django.conf import settings
from django_pandas.io import read_frame

from edc_metadata.constants import MISSED, REQUIRED
from edc_metadata.models import RequisitionMetadata

from ..constants import (
    PANEL_NOT_EXPECTED,
    REQUISITION_NOT_KEYED,
    RESOLVER_MISS,
    VISIT_NOT_FOUND,
)
from ..models import Result

__all__ = ["get_df_orphan_results"]

# a result carries the timepoint but not the schedule it belongs to,
# so the related visit supplies both. Do not read the schedule from
# settings: `ResultImporter.df_related_visits` hardcodes one schedule
# name, and a subject on any other would be bucketed wrongly
VISIT_KEY = ("subject_identifier", "visit_code", "visit_code_sequence")

METADATA_KEY = (
    "subject_identifier",
    "visit_schedule_name",
    "schedule_name",
    "visit_code",
    "visit_code_sequence",
    "panel_name",
)

# entry_status values meaning the requisition was expected here and has
# not been keyed. REQUIRED is stored, and reads as "New" in the admin
NOT_KEYED_STATUSES = (REQUIRED, MISSED)

ORPHAN_FRAME_COLUMNS = (
    # bucket
    "bucket",
    "entry_status",
    # identity
    "subject_identifier",
    "screening_identifier",
    "visit_schedule_name",
    "schedule_name",
    "visit_code",
    "visit_code_sequence",
    "panel_name",
    "utestid",
    # the requisition to link to, where one exists
    "requisition_id",
    "requisition_identifier",
    "drawn_datetime",
    "requisition_datetime",
    # why the importer missed it
    "specimen_collected_datetime",
    "order_datetime",
    "visit_datetime",
    "days_from_visit",
    # the imported result
    "result_id",
    "result_value",
    "units",
    "result_datetime",
    "source_file",
    "subject_visit_id",
)


def get_df_orphan_results() -> pd.DataFrame:
    """Return a trial-wide dataframe of imported results that carry no
    requisition, bucketed by what has to happen to each.

    One row per orphaned result. A data manager keys a requisition, not
    an analyte, so group by subject, timepoint and panel for the size of
    the work:

        df.groupby(
            ["subject_identifier", "visit_code", "visit_code_sequence",
             "panel_name"]
        ).ngroups

    `bucket` is one of:

    `resolver_miss`
        A requisition already exists at this timepoint for this panel.
        `RequisitionModelMixin` constrains panel and related visit to be
        unique together, so it is the requisition, not a best guess.
        Nothing was missing, the importer's join failed: it matches the
        specimen datetime against the requisition and the related visit
        by exact equality. See `ResultImporter.resolve_requisitions`.
        These need no data manager, only a pass that writes the link.

    `requisition_not_keyed`
        No requisition here, and `RequisitionMetadata` says the panel
        was expected. This is the worklist.

    `panel_not_expected`
        No requisition here and the panel was not expected at this
        timepoint, or there is no metadata for it at all. Suspect the
        utest id to panel mapping rather than the data. See
        `get_mappings`.

    `visit_not_found`
        The result names a timepoint that no related visit matches, or
        names none at all. Nothing further can be said about it here.

    `days_from_visit` is signed and diagnostic only, nothing is matched
    on it. A specimen drawn before its visit is the screening draw
    captured at baseline, which the importer's exact date join cannot
    resolve.
    """
    df = get_df_orphans()
    if df.empty:
        return pd.DataFrame(columns=list(ORPHAN_FRAME_COLUMNS))
    df = df.merge(get_df_related_visits(), on=list(VISIT_KEY), how="left")
    df = df.merge(
        get_df_requisitions(), on=["subject_visit_id", "panel_name"], how="left"
    ).merge(get_df_requisition_metadata(), on=list(METADATA_KEY), how="left")
    df["bucket"] = get_bucket(df)
    df["days_from_visit"] = (
        df["specimen_collected_datetime"] - df["visit_datetime"]
    ).dt.days.astype("Int64")
    return (
        df.reindex(columns=list(ORPHAN_FRAME_COLUMNS))
        .sort_values(["bucket", "subject_identifier", "visit_code", "panel_name"])
        .reset_index(drop=True)
    )


def get_bucket(df: pd.DataFrame) -> pd.Series:
    """Return the bucket of each orphan, most actionable first."""
    return pd.Series(
        np.select(
            [
                df["subject_visit_id"].isna().to_numpy(dtype=bool),
                df["requisition_id"].notna().to_numpy(dtype=bool),
                df["entry_status"].isin(NOT_KEYED_STATUSES).to_numpy(dtype=bool),
            ],
            [VISIT_NOT_FOUND, RESOLVER_MISS, REQUISITION_NOT_KEYED],
            default=PANEL_NOT_EXPECTED,
        ),
        index=df.index,
        dtype="string",
    )


def get_df_orphans() -> pd.DataFrame:
    """Return the imported results carrying no requisition."""
    df = read_frame(
        Result.objects.filter(requisition__isnull=True)
        .values(
            "id",
            "subject_identifier",
            "screening_identifier",
            "visit_code",
            "visit_code_sequence",
            "panel_name",
            "utestid",
            "result_value",
            "units",
            "result_datetime",
            "specimen_collected_datetime",
            "order_datetime",
            "source_file",
        )
        .all(),
        verbose=False,
    ).rename(columns={"id": "result_id"})
    if df.empty:
        return df
    return normalize_keys(df).reset_index(drop=True)


def get_df_related_visits() -> pd.DataFrame:
    """Return the timepoint of every related visit.

    The related visit, not the result, supplies `visit_schedule_name`
    and `schedule_name`, which `RequisitionMetadata` is keyed on.
    """
    model_cls = django_apps.get_model(settings.SUBJECT_VISIT_MODEL)
    df = read_frame(
        model_cls.objects.values(
            "id",
            "subject_identifier",
            "visit_schedule_name",
            "schedule_name",
            "visit_code",
            "visit_code_sequence",
            "report_datetime",
        ).all(),
        verbose=False,
    ).rename(columns={"id": "subject_visit_id", "report_datetime": "visit_datetime"})
    if df.empty:
        return df
    df["subject_visit_id"] = df["subject_visit_id"].astype("string")
    return normalize_keys(df).reset_index(drop=True)


def get_df_requisitions() -> pd.DataFrame:
    """Return every requisition, keyed by related visit and panel.

    `RequisitionModelMixin.Meta` constrains panel and related visit to
    be unique together, so this key can match at most one requisition.
    """
    model_cls = django_apps.get_model(settings.SUBJECT_REQUISITION_MODEL)
    visit_attr = model_cls.related_visit_model_attr()
    df = read_frame(
        model_cls.objects.values(
            "id",
            visit_attr,
            "panel__name",
            "requisition_identifier",
            "drawn_datetime",
            "requisition_datetime",
        ).all(),
        verbose=False,
    ).rename(
        columns={
            "id": "requisition_id",
            visit_attr: "subject_visit_id",
            "panel__name": "panel_name",
        }
    )
    if df.empty:
        return df
    for col in ["requisition_id", "subject_visit_id", "panel_name"]:
        df[col] = df[col].astype("string").str.strip().replace("", pd.NA)
    return df.reset_index(drop=True)


def get_df_requisition_metadata() -> pd.DataFrame:
    """Return whether a requisition was expected at each timepoint.

    KEYED rows are kept rather than filtered out. They do not change
    any bucket, but `entry_status` reading KEYED where no requisition
    was found is worth seeing: the metadata and the requisition
    disagree.
    """
    df = read_frame(
        RequisitionMetadata.objects.values(*METADATA_KEY, "entry_status").all(),
        verbose=False,
    )
    if df.empty:
        return df
    df["entry_status"] = df["entry_status"].astype("string")
    df["panel_name"] = df["panel_name"].astype("string").str.strip().replace("", pd.NA)
    return normalize_keys(df).reset_index(drop=True)


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    """Return `df` with the timepoint key in comparable dtypes.

    A null `visit_code_sequence` is a scheduled visit, which every
    other model stores as 0.
    """
    for col in ["subject_identifier", "visit_code", "visit_schedule_name", "schedule_name"]:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip().replace("", pd.NA)
    if "panel_name" in df.columns:
        df["panel_name"] = df["panel_name"].astype("string").str.strip().replace("", pd.NA)
    df["visit_code_sequence"] = (
        pd.to_numeric(df["visit_code_sequence"], errors="coerce").fillna(0).astype("Int64")
    )
    return df
