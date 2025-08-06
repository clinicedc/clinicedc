import pandas as pd
from django.apps import apps as django_apps
from django_pandas.io import read_frame

from edc_appointment.constants import NEW_APPT

from ..utils import convert_dates_from_model


def get_appointments(
    subject_identifiers: list[str] | None = None,
    normalize: bool | None = None,
    localize: bool | None = None,
):
    normalize = True if normalize is None else normalize
    localize = True if localize is None else localize
    model_cls = django_apps.get_model("edc_appointment.appointment")
    opts = {}
    if subject_identifiers:
        opts = dict(subject_identifier__in=subject_identifiers)
    df = read_frame(model_cls.objects.filter(**opts), verbose=False)
    df = convert_dates_from_model(df, model_cls, normalize=normalize, localize=localize)
    df = df.rename(columns={"id": "appointment_id", "site": "site_id"})
    df["visit_code_str"] = df["visit_code"]
    df = df[
        [
            "appointment_id",
            "subject_identifier",
            "appt_datetime",
            "appt_reason",
            "appt_status",
            "appt_timing",
            "appt_type",
            "appt_type_other",
            "site_id",
            "timepoint",
            "timepoint_datetime",
            "visit_code",
            "visit_code_sequence",
            "visit_code_str",
        ]
    ]
    # convert visit_code to float using visit_code_sequence
    df["visit_code"] = df["visit_code"].astype(float)
    df["visit_code_sequence"] = df["visit_code_sequence"].astype(float)
    df["appt_datetime"] = df["appt_datetime"].apply(pd.to_datetime)
    df["visit_code_sequence"] = df["visit_code_sequence"].apply(
        lambda x: x / 10.0 if x > 0.0 else 0.0
    )
    df["visit_code"] = df["visit_code"] + df["visit_code_sequence"]

    # next visit
    df_next = df[df.appt_status == NEW_APPT].copy()
    df_next = df_next.groupby("subject_identifier").agg(
        {"visit_code": "min", "appt_datetime": "min"}
    )
    df_next = df_next.rename(
        columns={"visit_code": "next_visit_code", "appt_datetime": "next_appt_datetime"}
    )
    if localize:
        df["appt_datetime"] = df["appt_datetime"].dt.tz_localize(None)
    if normalize:
        df["appt_datetime"] = df["appt_datetime"].dt.normalize()
    df_next["next_visit_code_str"] = (
        df_next["next_visit_code"].astype("int64").apply(lambda x: str(x))
    )
    df_next = df_next.reset_index()
    df = df.merge(df_next, on="subject_identifier", how="left")
    return df
