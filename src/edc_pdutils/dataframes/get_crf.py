from __future__ import annotations

import pandas as pd
from django.apps import apps as django_apps
from django.contrib.sites.models import Site
from django_pandas.io import read_frame

from edc_pdutils.constants import SYSTEM_COLUMNS

from .get_subject_visit import get_subject_visit
from .utils import (
    convert_dates_from_model,
    convert_numerics_from_model,
    convert_timedelta_from_model,
)


def get_crf(
    model: str | None = None,
    subject_visit_model: str | None = None,
    drop_columns: list[str] | None = None,
) -> pd.DataFrame:
    model_cls = django_apps.get_model(model)
    qs = model_cls.objects.all()
    df = read_frame(qs)
    df = df.rename(columns={"subject_visit": "subject_visit_id"})
    # move system columns to end
    df = df[[col for col in df.columns if col not in SYSTEM_COLUMNS] + SYSTEM_COLUMNS]
    if drop_columns:
        df = df.drop(columns=drop_columns)
    if subject_visit_model:
        df_subject_visit = get_subject_visit(subject_visit_model)
        df = pd.merge(
            df_subject_visit,
            df,
            on="subject_visit_id",
            how="right",
            suffixes=("", "_subject_visit"),
        )
        df = df.reset_index(drop=True)
    else:
        # remap site
        sites = {obj.domain: obj.id for obj in Site.objects.all()}
        df["site"] = df["site"].map(sites)
    df = convert_numerics_from_model(df, model_cls)
    df = convert_dates_from_model(df, model_cls)
    df = convert_timedelta_from_model(df, model_cls)
    return df
