from __future__ import annotations

import pandas as pd
from django.apps import apps as django_apps
from django.conf import settings
from django.db import models
from django_pandas.io import read_frame

from ..utils import get_decimal_places, get_result_models_by_panel_name, get_utest_ids

__all__ = ["get_df_result_crfs"]

CRF_COLUMNS = (
    "subject_identifier",
    "visit_code",
    "visit_code_sequence",
    "visit_datetime",
    "panel_name",
    "crf_model",
    "crf_id",
    "subject_visit_id",
    "requisition_id",
    "utestid",
    "crf_value",
    "crf_units",
    "crf_abnormal",
    "decimal_places",
)


def get_df_result_crfs() -> pd.DataFrame:
    """Return a long dataframe of every result CRF in the trial, one
    row per CRF instance per utest id.

    Rows are kept where the value is blank, so the frame is a complete
    grid of what could have been keyed rather than only what was. See
    `get_df_result_comparison`, which reconciles this grid against the
    imported results.

    The result CRFs come from `get_result_models_by_panel_name()`, the
    registry of models declaring a `lab_panel`, so this covers whatever
    the deployment has installed rather than a hardcoded list.
    """
    frames = [
        get_df_result_crf(model_cls, panel_name)
        for panel_name, model_cls in get_result_models_by_panel_name().items()
    ]
    frames = [df for df in frames if not df.empty]
    if not frames:
        return pd.DataFrame(columns=list(CRF_COLUMNS))
    df = pd.concat(frames, ignore_index=True)
    df = df.merge(get_df_subject_visit(), on="subject_visit_id", how="left")
    return df[list(CRF_COLUMNS)].reset_index(drop=True)


def get_df_result_crf(model_cls: type[models.Model], panel_name: str) -> pd.DataFrame:
    """Return the long dataframe for one result CRF model."""
    utest_ids = get_utest_ids(model_cls)
    field_names = {fld_cls.name for fld_cls in model_cls._meta.get_fields()}
    visit_attr = model_cls.related_visit_model_attr()
    families = {
        "crf_value": [f"{utest_id}_value" for utest_id in utest_ids],
        "crf_units": [
            f"{utest_id}_units"
            for utest_id in utest_ids
            if _has(field_names, utest_id, "units")
        ],
        "crf_abnormal": [
            f"{utest_id}_abnormal"
            for utest_id in utest_ids
            if _has(field_names, utest_id, "abnormal")
        ],
    }
    id_vars = ["crf_id", "subject_visit_id", "requisition_id"]
    df_wide = read_frame(
        model_cls.objects.values(
            "id",
            visit_attr,
            "requisition",
            *[col for cols in families.values() for col in cols],
        ).all(),
        verbose=False,
    ).rename(
        columns={
            "id": "crf_id",
            visit_attr: "subject_visit_id",
            "requisition": "requisition_id",
        }
    )
    if df_wide.empty:
        return pd.DataFrame(columns=[*id_vars, "utestid", *families])
    for col in id_vars:
        df_wide[col] = df_wide[col].astype("string").str.strip().replace("", pd.NA)

    df = None
    for value_name, cols in families.items():
        if not cols:
            continue
        suffix = f"_{value_name.removeprefix('crf_')}"
        melted = df_wide.melt(
            id_vars=id_vars, value_vars=cols, var_name="utestid", value_name=value_name
        )
        melted["utestid"] = melted["utestid"].str.removesuffix(suffix).astype("string")
        df = melted if df is None else df.merge(melted, on=[*id_vars, "utestid"], how="left")
    for value_name in families:
        if value_name not in df.columns:
            df[value_name] = pd.NA
    return df.assign(
        panel_name=panel_name,
        crf_model=model_cls._meta.label_lower,
        crf_value=lambda d: pd.to_numeric(d["crf_value"], errors="coerce").astype("float64"),
        crf_units=lambda d: d["crf_units"].astype("string").fillna(""),
        crf_abnormal=lambda d: d["crf_abnormal"].astype("string").fillna(""),
        decimal_places=lambda d: (
            d["utestid"].map(get_decimal_places(model_cls)).astype("Int64")
        ),
    )


def get_df_subject_visit() -> pd.DataFrame:
    """Return the subject and timepoint of every related visit."""
    model_cls = django_apps.get_model(settings.SUBJECT_VISIT_MODEL)
    df = read_frame(
        model_cls.objects.values(
            "id",
            "subject_identifier",
            "visit_code",
            "visit_code_sequence",
            "report_datetime",
        ).all(),
        verbose=False,
    ).rename(
        columns={
            "id": "subject_visit_id",
            "report_datetime": "visit_datetime",
        }
    )
    for col in ["subject_visit_id", "subject_identifier", "visit_code"]:
        df[col] = df[col].astype("string").str.strip().replace("", pd.NA)
    return df.reset_index(drop=True)


def _has(field_names: set[str], utest_id: str, suffix: str) -> bool:
    """Return True if this utest id has a field with this suffix.

    A result CRF built by `result_model_mixin_factory` has no
    `_abnormal` field, only one built by
    `reportable_result_model_mixin_factory` does.
    """
    return f"{utest_id}_{suffix}" in field_names
