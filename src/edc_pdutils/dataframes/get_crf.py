from __future__ import annotations

import pandas as pd
from django.apps import apps as django_apps
from django.contrib.sites.models import Site
from django.db import models
from django_pandas.io import read_frame

from edc_model_to_dataframe.read_frame_edc import read_frame_edc
from edc_registration.models import RegisteredSubject

from ..constants import SYSTEM_COLUMNS
from ..utils import (
    convert_dates_from_model,
    convert_numbers_to_nullable_dtype,
    convert_timedelta_from_model,
)
from .get_subject_visit import get_subject_visit


def get_crf(
    model: str | None = None,
    subject_visit_model: str | None = None,
    drop_columns: list[str] | None = None,
    subject_identifiers: list[str] | None = None,
    normalize: bool | None = None,
    localize: bool | None = None,
    read_verbose: bool | None = None,
    drop_sys_columns: bool | None = None,
    drop_action_item_columns: bool | None = None,
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
    df = df.rename(columns={"site": "site_id", "subject_visit": "subject_visit_id"})

    if "subject_visit_id" not in df.columns:
        raise ValueError("This is not a CRF. Requires col subject_visit_id.")

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

    df["subject_visit_id_original"] = df["subject_visit_id"]
    df["subject_visit_id"] = df["subject_visit_id"].astype(str)
    for field in model_cls._meta.get_fields():
        if isinstance(field, models.ManyToManyField):
            df_m2m = (
                read_frame_edc(
                    qs,
                    read_frame_verbose=False,
                    drop_sys_columns=drop_sys_columns,
                    drop_action_item_columns=drop_action_item_columns,
                )
                .sort_values(["subject_identifier", "visit_code"])
                .reset_index(drop=True)
            )
            df_m2m["subject_visit_id"] = df_m2m["subject_visit_id"].astype(str)
            df = df.merge(
                df_m2m[["subject_visit_id", field.name]],
                on="subject_visit_id",
                how="left",
            )
    df = df.drop(columns=["subject_visit_id"])
    df = df.rename(columns={"subject_visit_id_original": "subject_visit_id"})

    # move system columns to end
    df = df[[col for col in df.columns if col not in SYSTEM_COLUMNS] + SYSTEM_COLUMNS]
    if drop_columns:
        df = df.drop(columns=drop_columns)

    # add demographics
    df_rs = read_frame(
        RegisteredSubject.objects.values(
            "subject_identifier", "gender", "dob", "ethnicity"
        ).all(),
        verbose=read_verbose,
    )
    df = df.merge(df_rs, on="subject_identifier", how="left")
    first_cols = [
        "subject_identifier",
        "gender",
        "dob",
        "ethnicity",
        "appointment_id",
        "subject_visit_id",
    ]
    df = df[
        [
            *first_cols,
            *[col for col in df.columns if col not in first_cols],
        ]
    ]

    # convert values to ...
    # df = convert_numerics_from_model(df, model_cls)
    df = convert_numbers_to_nullable_dtype(df)
    df = convert_dates_from_model(df, model_cls, normalize=normalize, localize=localize)
    df = convert_timedelta_from_model(df, model_cls)
    df = df.replace("", pd.NA).fillna(pd.NA).reset_index(drop=True)
    return df
