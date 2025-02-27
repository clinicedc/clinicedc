import pandas as pd
from django.apps import apps as django_apps
from django_pandas.io import read_frame
from edc_pdutils.utils import convert_dates_from_model

from ...constants import NEW_APPT
from ...utils import get_appointment_model_cls


def get_appointment_df(
    normalize: bool | None = None,
    localize: bool | None = None,
    values: list[str] | None = None,
    site_id: int | None = None,
) -> pd.DataFrame:
    normalize = True if normalize is None else normalize
    localize = True if localize is None else localize
    appointment_model_cls = get_appointment_model_cls()
    appointment_type_model_cls = django_apps.get_model("edc_appointment.appointmenttype")
    opts = {}
    if site_id:
        opts = {"site_id": site_id}
    if values:
        df_appt = read_frame(
            appointment_model_cls.objects.values(*values).filter(**opts), verbose=False
        )
    else:
        df_appt = read_frame(appointment_model_cls.objects.filter(**opts), verbose=False)
    df_appt = convert_dates_from_model(
        df_appt, appointment_model_cls, normalize=normalize, localize=localize
    )
    df_appt = df_appt.rename(
        columns={
            "id": "appointment_id",
            "site": "site_id",
        }
    )
    # rework visit code
    df_appt["visit_code_str"] = df_appt["visit_code"]
    df_appt["visit_code"] = df_appt["visit_code"].astype(float)
    df_appt["visit_code_sequence"] = df_appt["visit_code_sequence"].astype(float)
    df_appt["visit_code_sequence"] = df_appt["visit_code_sequence"].apply(
        lambda x: x / 10.0 if x > 0.0 else 0.0
    )
    df_appt["visit_code"] = df_appt["visit_code"] + df_appt["visit_code_sequence"]

    # merge in baseline_datetime
    df_baseline = df_appt.copy()
    df_baseline = df_baseline[(df_baseline["visit_code"] == 1000.0)]
    df_baseline = df_baseline.rename(columns={"appt_datetime": "baseline_datetime"})
    df_baseline = df_baseline[["subject_identifier", "baseline_datetime"]]
    df_appt = df_appt.merge(df_baseline, on="subject_identifier", how="left")

    # merge in last appointment
    df_last = (
        df_appt[df_appt.appt_status != NEW_APPT]
        .groupby("subject_identifier")
        .agg({"visit_code": "max", "appt_datetime": "max"})
    ).copy()
    df_last = df_last.rename(
        columns={"visit_code": "endline_visit_code", "appt_datetime": "last_appt_datetime"}
    )
    df_last["endline_visit_code_str"] = (
        df_last["endline_visit_code"].astype("int64").apply(lambda x: str(x))
    )
    df_last = df_last.reset_index()
    df_appt = df_appt.merge(df_last, on="subject_identifier", how="left")

    # merge in next appointment
    df_next = (
        df_appt[df_appt.appt_status == NEW_APPT]
        .groupby("subject_identifier")
        .agg({"visit_code": "min", "appt_datetime": "min"})
    ).copy()
    df_next = df_next.rename(
        columns={"visit_code": "next_visit_code", "appt_datetime": "next_appt_datetime"}
    )
    df_next["next_visit_code_str"] = (
        df_next["next_visit_code"].astype("int64").apply(lambda x: str(x))
    )
    df_next = df_next.reset_index()
    df_appt = df_appt.merge(df_next, on="subject_identifier", how="left")

    # merge in appt type
    df1 = read_frame(appointment_type_model_cls.objects.values("id", "name").all())
    df1 = df1.rename(columns={"id": "appt_type"})
    df_appt = df_appt.merge(df1, on="appt_type", how="left")
    df_appt = df_appt.drop(columns=["appt_type"])
    df_appt = df_appt.rename(columns={"name": "appt_type"})

    return df_appt
