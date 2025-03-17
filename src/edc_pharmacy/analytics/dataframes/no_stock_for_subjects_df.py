from __future__ import annotations

import pandas as pd
from django_pandas.io import read_frame
from edc_registration.models import RegisteredSubject
from edc_visit_schedule.models import SubjectScheduleHistory

from ...models import Allocation, Stock
from .get_next_scheduled_visit_for_subjects_df import (
    get_next_scheduled_visit_for_subjects_df,
)


def no_stock_for_subjects_df() -> pd.DataFrame:
    df_schedule = read_frame(
        SubjectScheduleHistory.objects.values(
            "subject_identifier",
            "visit_schedule_name",
            "schedule_name",
            "offschedule_datetime",
        ).all()
    )

    df_schedule = df_schedule[
        (df_schedule.visit_schedule_name == "visit_schedule")
        & (df_schedule.schedule_name == "schedule")
        & df_schedule.offschedule_datetime.isna()
    ]
    df_schedule.reset_index(drop=True, inplace=True)

    df_stock_on_site = read_frame(
        Stock.objects.values("code", "allocation").filter(
            confirmed_at_site=True, dispensed=False
        ),
        verbose=False,
    )

    df_allocation = read_frame(
        Allocation.objects.values("id", "registered_subject").all(), verbose=False
    )
    df_rs = read_frame(
        RegisteredSubject.objects.values("id", "subject_identifier").all(), verbose=False
    )
    df_allocation = df_allocation.merge(
        df_rs[["id", "subject_identifier"]],
        how="left",
        left_on="registered_subject",
        right_on="id",
        suffixes=["_allocation", "_rs"],
    )

    df_stock_on_site = df_stock_on_site.merge(
        df_allocation[["id_allocation", "subject_identifier"]],
        how="left",
        left_on="allocation",
        right_on="id_allocation",
    )

    df = pd.merge(
        df_schedule[["subject_identifier", "offschedule_datetime"]],
        df_stock_on_site,
        on="subject_identifier",
        how="left",
    )
    df = (
        df[df.code.isna()][["subject_identifier"]]
        .sort_values(by=["subject_identifier"])
        .reset_index(drop=True)
    )

    df_appt = get_next_scheduled_visit_for_subjects_df()
    df_appt = df_appt[
        ["subject_identifier", "site_id", "visit_code", "appt_datetime", "baseline_datetime"]
    ].copy()
    df_appt.reset_index(drop=True, inplace=True)

    df = df.merge(df_appt, how="left", on="subject_identifier")
    df = df[(df.appt_datetime.notna())]
    df.reset_index(drop=True, inplace=True)

    utc_now = pd.Timestamp.utcnow().tz_localize(None)
    df["relative_days"] = (df.appt_datetime - utc_now).dt.days
    df_final = df[(df.relative_days >= -105)].copy()
    df_final["appt_date"] = df_final.appt_datetime.dt.date
    df_final.reset_index(drop=True, inplace=True)
    return df_final
