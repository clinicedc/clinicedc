from __future__ import annotations

import numpy as np
import pandas as pd
from clinicedc_constants import NO
from django.apps import apps as django_apps
from django.conf import settings
from django_pandas.io import read_frame

from edc_metadata.constants import MISSED, REQUIRED
from edc_metadata.models import RequisitionMetadata

from ..constants import (
    MAX_DAYS_BEFORE_BASELINE,
    ON_OR_BEFORE_BASELINE,
    PANEL_NOT_EXPECTED,
    PANEL_UNKNOWN,
    REQUISITION_NOT_KEYED,
    RESOLVER_MISS,
    VISIT_NOT_FOUND,
)
from ..models import Result
from ..utils import get_requisition_panel_name_map
from .staleness import stamp_pulled_datetime

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
    "requisition_panel_name",
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
    "requisition_panel_name",
    "utestid",
    # the requisition to link to, where one exists
    "requisition_id",
    "requisition_identifier",
    "drawn_datetime",
    "requisition_datetime",
    "result_expected",
    "result_not_expected_reason",
    "result_expected_conflict",
    # why the importer missed it
    "specimen_collected_datetime",
    "order_datetime",
    "visit_datetime",
    "days_from_visit",
    # the timepoint this result would be assigned to, and the
    # requisition waiting there. Proposed, never written
    "candidate_rule",
    "candidate_subject_visit_id",
    "candidate_visit_code",
    "candidate_requisition_id",
    "candidate_requisition_identifier",
    "baseline_visit_datetime",
    "days_before_baseline",
    # the imported result
    "result_id",
    "result_value",
    "units",
    "result_datetime",
    "source_file",
    "subject_visit_id",
)


def get_df_orphan_results(max_days_before_baseline: int | None = None) -> pd.DataFrame:
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

    `panel_unknown`
        The result carries no panel at all, because its utest id is in
        no registered panel. `resolve_requisitions` joins on utest id
        against requisitions keyed through `df_utestid`, so such a
        result cannot match a requisition by any date. The utest id to
        panel mapping is the fix, see `get_mappings`, not the data.

    `panel_not_expected`
        The result has a panel, but no requisition here and no metadata
        saying one was due at this timepoint. An ad hoc draw, or a panel
        the schedule does not call for here.

    `visit_not_found`
        The result names a timepoint that no related visit matches, or
        names none at all. Nothing further can be said about it here.

    The buckets are ordered, and a result can be in more than one
    state: every row with no panel may also have no timepoint. Cross
    tabulate `panel_name.isna()` against `subject_visit_id.isna()` for
    the overlap rather than reading the buckets as disjoint causes.

    `candidate_rule` proposes a timepoint for a result that found none.
    See `add_baseline_candidate`. It is a proposal, nothing is written.

    `days_from_visit` is signed and diagnostic only, nothing is matched
    on it. A specimen drawn before its visit is the screening draw
    captured at baseline, which the importer's exact date join cannot
    resolve.
    """
    df = get_df_orphans()
    if df.empty:
        return stamp_pulled_datetime(pd.DataFrame(columns=list(ORPHAN_FRAME_COLUMNS)))
    df = df.merge(get_df_related_visits(), on=list(VISIT_KEY), how="left")
    df = df.merge(
        get_df_requisitions(),
        on=["subject_visit_id", "requisition_panel_name"],
        how="left",
    ).merge(get_df_requisition_metadata(), on=list(METADATA_KEY), how="left")
    df["bucket"] = get_bucket(df)
    # the requisition says the lab will never report, yet here is a
    # result from the lab. Someone has to look at these
    df["result_expected_conflict"] = (df["result_expected"] == NO).fillna(False)
    df["days_from_visit"] = (
        df["specimen_collected_datetime"] - df["visit_datetime"]
    ).dt.days.astype("Int64")
    df = add_baseline_candidate(df, max_days_before_baseline)
    df = (
        df.reindex(columns=list(ORPHAN_FRAME_COLUMNS))
        .sort_values(["bucket", "subject_identifier", "visit_code", "panel_name"])
        .reset_index(drop=True)
    )
    return stamp_pulled_datetime(df)


def add_baseline_candidate(
    df: pd.DataFrame, max_days_before_baseline: int | None = None
) -> pd.DataFrame:
    """Propose the baseline timepoint for a result drawn before the
    subject had any visit.

    A specimen collected on or before a subject's first visit cannot
    belong to a later timepoint, so baseline is the only candidate.
    That is a fact about the timeline, not a guess about dates, which
    is why nothing here needs a tolerance. It is bounded all the same:
    "on or before" alone would claim a specimen drawn a year earlier,
    so `max_days_before_baseline` caps how far back, defaulting to
    `MAX_DAYS_BEFORE_BASELINE`.

    Baseline is the earliest related visit by report datetime rather
    than a hardcoded visit code, so a subject on any schedule is
    covered. Only rows that found no timepoint of their own are
    proposed for, and only where the subject is known: with no subject
    there is no baseline to compare against.

    `candidate_requisition_id` is the requisition already waiting at
    that timepoint for this panel, where one exists. Nothing is
    written. See `link_orphan_results` for the shape a writer takes.
    """
    max_days = (
        MAX_DAYS_BEFORE_BASELINE
        if max_days_before_baseline is None
        else max_days_before_baseline
    )
    df_baseline = get_df_baseline_visits()
    if df_baseline.empty:
        return df.assign(
            candidate_rule=pd.NA,
            candidate_subject_visit_id=pd.NA,
            candidate_visit_code=pd.NA,
            baseline_visit_datetime=pd.NaT,
            days_before_baseline=pd.NA,
            candidate_requisition_id=pd.NA,
            candidate_requisition_identifier=pd.NA,
        )
    df = df.merge(df_baseline, on="subject_identifier", how="left")
    proposed = (
        df["subject_visit_id"].isna()
        & df["subject_identifier"].notna()
        & df["specimen_collected_datetime"].notna()
        & (df["specimen_collected_datetime"] <= df["baseline_visit_datetime"])
        & (
            df["baseline_visit_datetime"] - df["specimen_collected_datetime"]
            <= pd.Timedelta(days=max_days)
        )
    ).fillna(False)
    df["days_before_baseline"] = (
        (df["baseline_visit_datetime"] - df["specimen_collected_datetime"])
        .dt.days.astype("Int64")
        .where(proposed)
    )
    df["candidate_rule"] = pd.Series(
        np.where(proposed, ON_OR_BEFORE_BASELINE, pd.NA), index=df.index, dtype="string"
    )
    df["candidate_subject_visit_id"] = df["baseline_subject_visit_id"].where(proposed)
    df["candidate_visit_code"] = df["baseline_visit_code"].where(proposed)
    return add_candidate_requisition(df)


def get_df_baseline_visits() -> pd.DataFrame:
    """Return each subject's earliest related visit."""
    df = get_df_related_visits()
    if df.empty:
        return df
    return (
        df.sort_values("visit_datetime")
        .drop_duplicates(subset=["subject_identifier"], keep="first")
        .loc[:, ["subject_identifier", "subject_visit_id", "visit_code", "visit_datetime"]]
        .rename(
            columns={
                "subject_visit_id": "baseline_subject_visit_id",
                "visit_code": "baseline_visit_code",
                "visit_datetime": "baseline_visit_datetime",
            }
        )
        .reset_index(drop=True)
    )


def add_candidate_requisition(df: pd.DataFrame) -> pd.DataFrame:
    """Return `df` with the requisition waiting at the candidate
    timepoint, where one exists.
    """
    df_requisitions = get_df_requisitions()
    if df_requisitions.empty:
        return df.assign(
            candidate_requisition_id=pd.NA, candidate_requisition_identifier=pd.NA
        )
    candidates = df_requisitions.loc[
        :,
        [
            "subject_visit_id",
            "requisition_panel_name",
            "requisition_id",
            "requisition_identifier",
        ],
    ].rename(
        columns={
            "subject_visit_id": "candidate_subject_visit_id",
            "requisition_id": "candidate_requisition_id",
            "requisition_identifier": "candidate_requisition_identifier",
        }
    )
    return df.merge(
        candidates, on=["candidate_subject_visit_id", "requisition_panel_name"], how="left"
    )


def get_bucket(df: pd.DataFrame) -> pd.Series:
    """Return the bucket of each orphan, most actionable first."""
    return pd.Series(
        np.select(
            [
                df["subject_visit_id"].isna().to_numpy(dtype=bool),
                df["panel_name"].isna().to_numpy(dtype=bool),
                df["requisition_id"].notna().to_numpy(dtype=bool),
                df["entry_status"].isin(NOT_KEYED_STATUSES).to_numpy(dtype=bool),
            ],
            [VISIT_NOT_FOUND, PANEL_UNKNOWN, RESOLVER_MISS, REQUISITION_NOT_KEYED],
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
    df = normalize_keys(coerce_datetimes(df))
    # the panel a result was drawn under, which is not always the panel
    # it is reported under. See `get_requisition_panel_name_map`
    df["requisition_panel_name"] = df["panel_name"].replace(get_requisition_panel_name_map())
    return df.reset_index(drop=True)


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
    return normalize_keys(coerce_datetimes(df)).reset_index(drop=True)


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
            "result_expected",
            "result_not_expected_reason",
        ).all(),
        verbose=False,
    ).rename(
        columns={
            "id": "requisition_id",
            visit_attr: "subject_visit_id",
            "panel__name": "requisition_panel_name",
        }
    )
    if df.empty:
        return df
    for col in ["requisition_id", "subject_visit_id", "requisition_panel_name"]:
        df[col] = df[col].astype("string").str.strip().replace("", pd.NA)
    for col in ["result_expected", "result_not_expected_reason"]:
        df[col] = df[col].astype("string")
    return df.reset_index(drop=True)


def get_df_requisition_metadata() -> pd.DataFrame:
    """Return whether a requisition was expected at each timepoint.

    KEYED rows are kept rather than filtered out. They do not change
    any bucket, but `entry_status` reading KEYED where no requisition
    was found is worth seeing: the metadata and the requisition
    disagree.
    """
    df = read_frame(
        RequisitionMetadata.objects.values(
            *[col.replace("requisition_panel_name", "panel_name") for col in METADATA_KEY],
            "entry_status",
        ).all(),
        verbose=False,
    )
    if df.empty:
        return df
    df = df.rename(columns={"panel_name": "requisition_panel_name"})
    df["entry_status"] = df["entry_status"].astype("string")
    return normalize_keys(df).reset_index(drop=True)


def coerce_datetimes(df: pd.DataFrame) -> pd.DataFrame:
    """Return `df` with its datetime columns as datetimes.

    A column that is null for every row comes back from `read_frame` as
    object dtype, which cannot be subtracted from a datetime. That is
    not hypothetical: a result with no `specimen_collected_datetime` is
    exactly the kind of row this report exists to surface.
    """
    for col in [
        "result_datetime",
        "specimen_collected_datetime",
        "order_datetime",
        "visit_datetime",
    ]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")
    return df


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    """Return `df` with the timepoint key in comparable dtypes.

    A null `visit_code_sequence` is a scheduled visit, which every
    other model stores as 0.
    """
    for col in ["subject_identifier", "visit_code", "visit_schedule_name", "schedule_name"]:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip().replace("", pd.NA)
    for col in ["panel_name", "requisition_panel_name"]:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip().replace("", pd.NA)
    df["visit_code_sequence"] = (
        pd.to_numeric(df["visit_code_sequence"], errors="coerce").fillna(0).astype("Int64")
    )
    return df
