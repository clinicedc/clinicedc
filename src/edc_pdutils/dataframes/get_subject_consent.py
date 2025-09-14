import numpy as np
import pandas as pd
from django.apps import apps as django_apps
from django.db.models import Model
from django_pandas.io import read_frame

from edc_constants.constants import FEMALE, MALE

from ..utils import convert_dates_from_model


def get_subject_consent(
    model: str | None = None,
    model_cls: type[Model] | None = None,
    subject_identifiers: list[str] | None = None,
    extra_columns: list[str] | None = None,
    normalize: bool | None = None,
    localize: bool | None = None,
) -> pd.DataFrame:
    extra_columns = extra_columns or []
    normalize = True if normalize is None else normalize
    localize = True if localize is None else localize
    model_cls = model_cls or django_apps.get_model(model)
    value_cols = [
        "subject_identifier",
        "gender",
        "dob",
        "screening_identifier",
        "consent_datetime",
        "report_datetime",
        "created",
        "user_created",
        "version",
        "site",
    ]
    value_cols = list(set(value_cols + extra_columns))
    if subject_identifiers:
        qs_consent = model_cls.objects.values(*value_cols).filter(
            subject_identifier__in=subject_identifiers
        )
    else:
        qs_consent = model_cls.objects.values(*value_cols).all()
    df = read_frame(qs_consent, verbose=False)
    df = df.rename(columns={"site": "site_id"})
    df["gender"] = pd.Categorical(df["gender"], categories=[FEMALE, MALE], ordered=True)
    for col in ["dob", "consent_datetime", "report_datetime", "created"]:
        df[col] = df[col].apply(pd.to_datetime, errors="coerce")

    df = convert_dates_from_model(df, model_cls, normalize=normalize, localize=localize)
    if not df["consent_datetime"].empty:
        df["age_in_years"] = df["consent_datetime"].dt.year - df["dob"].dt.year
        df["age_in_years"] = df["age_in_years"].astype("int64")
    else:
        df["age_in_years"] = np.nan

    df = df.sort_values(by="subject_identifier")
    df = df.reset_index(drop=True)
    return df
