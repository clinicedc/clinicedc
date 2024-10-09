from __future__ import annotations

import pandas as pd
from django.apps import apps as django_apps
from django.contrib.sites.models import Site
from django_pandas.io import read_frame

from ..constants import SYSTEM_COLUMNS
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
    subject_identifiers: list[str] | None = None,
    normalize: bool | None = None,
    localize: bool | None = None,
    read_verbose: bool | None = None,
) -> pd.DataFrame:
    """Return a dataframe of CRF model.

    Merge with subject visit model of model lanel_lower
    id provided.

    Rename columns site to site_id, subject_visit to subject_visit_id
    """

    normalize = True if normalize is None else normalize
    localize = True if localize is None else localize
    read_verbose = True if read_verbose is None else read_verbose
    model_cls = django_apps.get_model(model)
    if subject_identifiers:
        qs = model_cls.objects.filter(
            subject_visit__subject_identifier__in=subject_identifiers
        )
    else:
        qs = model_cls.objects.all()
    df = read_frame(qs, verbose=read_verbose)
    if read_verbose:
        sites = {obj.domain: obj.id for obj in Site.objects.all()}
        df["site"] = df["site"].map(sites)
    df = df.rename(columns={"site": "site_id"})

    # convert values to ...
    df = convert_numerics_from_model(df, model_cls)
    df = convert_dates_from_model(df, model_cls, normalize=normalize, localize=localize)
    df = convert_timedelta_from_model(df, model_cls)

    df = df.rename(columns={"subject_visit": "subject_visit_id"})
    if subject_visit_model:
        df = df.reset_index(drop=True)
        df_subject_visit = get_subject_visit(
            subject_visit_model, subject_identifiers=subject_identifiers
        )
        df = pd.merge(
            df_subject_visit,
            df,
            on="subject_visit_id",
            how="right",
            suffixes=("", "_subject_visit"),
        )
        df = df.drop(columns=[col for col in df.columns if col.endswith("_subject_visit")])
        df = df.reset_index(drop=True)
    # move system columns to end
    df = df[[col for col in df.columns if col not in SYSTEM_COLUMNS] + SYSTEM_COLUMNS]
    if drop_columns:
        df = df.drop(columns=drop_columns)
    df = df.reset_index(drop=True)
    return df
