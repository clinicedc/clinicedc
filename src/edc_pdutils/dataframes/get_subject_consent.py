import pandas as pd
from django.apps import apps as django_apps
from django_pandas.io import read_frame


def get_subject_consent(model: str) -> pd.DataFrame:
    qs_consent = (
        django_apps.get_model(model)
        .objects.values(
            "subject_identifier", "gender", "dob", "screening_identifier", "consent_datetime"
        )
        .all()
    )
    df = read_frame(qs_consent)
    df["dob"] = df["dob"].apply(pd.to_datetime)
    df["consent_datetime"] = df["consent_datetime"].apply(pd.to_datetime)
    df["consent_datetime"] = df["consent_datetime"].dt.floor("d")
    df["age_in_years"] = df["consent_datetime"].dt.year - df["dob"].dt.year
    df.sort_values(by=["subject_identifier"])
    df.reset_index(drop=True, inplace=True)
    return df
