from __future__ import annotations

import pandas as pd
from django_pandas.io import read_frame

from edc_visit_schedule.models import SubjectScheduleHistory

from ...models import Stock, StorageBinItem
from ...utils import get_imp_schedule_names
from .get_next_scheduled_visit_for_subjects_df import (
    get_next_scheduled_visit_for_subjects_df,
)


def remove_exact_duplicates(s):
    seen = set()
    result = []
    for item in s.split(","):
        if item not in seen:
            seen.add(item)
            result.append(item)
    return ",".join(result)


def stock_for_subjects_df() -> pd.DataFrame:

    visit_schedule_names, schedule_names = get_imp_schedule_names()

    df_schedule = read_frame(
        SubjectScheduleHistory.objects.values(
            "subject_identifier",
            "visit_schedule_name",
            "schedule_name",
            "offschedule_datetime",
        ).filter(
            visit_schedule_name__in=visit_schedule_names,
            schedule_name__in=schedule_names,
            offschedule_datetime__isnull=True,
        )
    )

    df_stock_on_site = read_frame(
        Stock.objects.values(
            "code", "allocation__registered_subject__subject_identifier"
        ).filter(confirmationatsiteitem__isnull=False, dispenseitem__isnull=True),
        verbose=False,
    ).rename(
        columns={"allocation__registered_subject__subject_identifier": "subject_identifier"}
    )

    df = pd.merge(
        df_schedule[["subject_identifier", "offschedule_datetime"]],
        df_stock_on_site,
        on="subject_identifier",
        how="left",
    ).fillna("")

    df_storage = read_frame(
        StorageBinItem.objects.values("stock__code", "storage_bin__name").filter(
            stock__code__in=df["code"].tolist(),
            storage_bin__in_use=True,
            stock__dispenseitem__isnull=True,
        )
    ).rename(columns={"stock__code": "code", "storage_bin__name": "bin"})

    df = df.merge(df_storage[["code", "bin"]], on="code", how="left").fillna("")

    df_codes = (
        df.groupby("subject_identifier")["code"]
        .agg(",".join)
        .reset_index()
        .sort_values(by=["subject_identifier"])
        .reset_index(drop=True)
    )

    df_bins = (
        df.groupby("subject_identifier")["bin"]
        .agg(",".join)
        .reset_index()
        .sort_values(by=["subject_identifier"])
        .reset_index(drop=True)
    )

    df = df_codes.merge(df_bins, on="subject_identifier", how="left")

    df_appt = get_next_scheduled_visit_for_subjects_df()
    df_appt = (
        df_appt[
            [
                "subject_identifier",
                "site_id",
                "visit_code",
                "appt_datetime",
                "baseline_datetime",
            ]
        ]
        .copy()
        .reset_index(drop=True)
    )

    df = df.merge(df_appt, how="left", on="subject_identifier")
    df = df[(df.appt_datetime.notna())].reset_index(drop=True)

    utc_now = pd.Timestamp.utcnow().tz_localize(None)
    df["relative_days"] = (df.appt_datetime - utc_now).dt.days
    # df = df[(df.relative_days >= -105)]
    df["appt_date"] = df.appt_datetime.dt.date
    df.loc[df["code"].str.strip() == "", "code"] = pd.NA
    df.loc[df["bin"].str.strip() == "", "bin"] = pd.NA
    df.loc[~df["bin"].isna(), "bin"] = df.loc[~df["bin"].isna(), "bin"].apply(
        remove_exact_duplicates
    )
    df = df.rename(columns={"code": "codes", "bin": "bins"}).reset_index(drop=True)
    return df
