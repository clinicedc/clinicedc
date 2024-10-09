import pandas as pd
from django.apps import apps as django_apps
from django_pandas.io import read_frame

from .utils import convert_dates_from_model


def get_subject_visit(
    model: str,
    subject_identifiers: list[str] | None = None,
    normalize: bool | None = None,
    localize: bool | None = None,
) -> pd.DataFrame:
    """Read subject visit django model.

    Converts visit_code to a float of visit_code + visit_code_sequence,
    For example:
        1000.0, 1000.1, ...
    The original string visit_code is renamed as visit_code_str.

    Adds baseline and last visit datetimes and last_visit_code
    """
    normalize = True if normalize is None else normalize
    localize = True if localize is None else localize
    model_cls = django_apps.get_model(model)
    if subject_identifiers:
        qs_subject_visit = model_cls.objects.filter(subject_identifier__in=subject_identifiers)
    else:
        qs_subject_visit = model_cls.objects.all()
    df = read_frame(qs_subject_visit, verbose=False)
    df = convert_dates_from_model(df, model_cls, normalize=normalize, localize=localize)
    df = df.rename(
        columns={
            "id": "subject_visit_id",
            "report_datetime": "visit_datetime",
            "site": "site_id",
            "appointment": "appointment_id",
        }
    )
    df["visit_code_str"] = df["visit_code"]
    df = df[
        [
            "subject_visit_id",
            "subject_identifier",
            "visit_code",
            "visit_code_sequence",
            "visit_datetime",
            "site_id",
            "visit_code_str",
            "reason",
            "reason_unscheduled",
            "reason_unscheduled_other",
            "reason_missed",
            "reason_missed_other",
            "appointment_id",
        ]
    ]
    # convert visit_code to float using visit_code_sequence
    df["visit_code"] = df["visit_code"].astype(float)
    df["visit_code_sequence"] = df["visit_code_sequence"].astype(float)
    df["visit_datetime"] = df["visit_datetime"].apply(pd.to_datetime)
    df["visit_code_sequence"] = df["visit_code_sequence"].apply(
        lambda x: x / 10.0 if x > 0.0 else 0.0
    )
    df["visit_code"] = df["visit_code"] + df["visit_code_sequence"]

    df_baseline_visit = df.copy()
    df_baseline_visit = df_baseline_visit[(df_baseline_visit["visit_code"] == 1000.0)]
    df_baseline_visit = df_baseline_visit.rename(
        columns={"visit_datetime": "baseline_datetime"}
    )
    df_baseline_visit = df_baseline_visit[["subject_identifier", "baseline_datetime"]]

    df = df.merge(df_baseline_visit, on="subject_identifier", how="left")

    # get last visitcode and last visit datetime
    df_last = (
        df[df.reason != "Missed visit"]
        .groupby("subject_identifier")
        .agg({"visit_code": "max", "visit_datetime": "max"})
    ).copy()
    df_last = df_last.rename(
        columns={"visit_code": "last_visit_code", "visit_datetime": "last_visit_datetime"}
    )
    df_last["last_visit_code_str"] = (
        df_last["last_visit_code"].astype("int64").apply(lambda x: str(x))
    )
    df_last = df_last.reset_index()
    df = df.merge(df_last, on="subject_identifier", how="left")
    df = df.sort_values(by=["subject_identifier", "visit_code"])
    df = df.reset_index(drop=True)
    return df
