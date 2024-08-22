import pandas as pd
from django.apps import apps as django_apps
from django_pandas.io import read_frame


def get_subject_consent(
    model: str, subject_identifiers: list[str] | None = None
) -> pd.DataFrame:
    model_cls = django_apps.get_model(model)
    value_cols = [
        "subject_identifier",
        "gender",
        "dob",
        "screening_identifier",
        "consent_datetime",
    ]
    if subject_identifiers:
        qs_consent = model_cls.objects.values(*value_cols).filter(
            subject_identifier__in=subject_identifiers
        )
    else:
        qs_consent = model_cls.objects.values(*value_cols).all()
    df = read_frame(qs_consent)
    df["dob"] = df["dob"].apply(pd.to_datetime)
    df["consent_datetime"] = df["consent_datetime"].apply(pd.to_datetime)
    if not df["consent_datetime"].empty:
        df["consent_datetime"] = df["consent_datetime"].dt.floor("d")
        df["age_in_years"] = df["consent_datetime"].dt.year - df["dob"].dt.year
    df.sort_values(by=["subject_identifier"])
    df.reset_index(drop=True, inplace=True)
    return df
