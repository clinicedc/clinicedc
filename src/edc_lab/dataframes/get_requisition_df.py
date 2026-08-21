import pandas as pd
from clinicedc_utils import convert_visit_code_to_float
from django.apps import apps as django_apps
from django.conf import settings
from django_pandas.io import read_frame

from ..constants import FINGER_PRICK
from ..lab import RequisitionPanel
from ..site_labs import site_labs

__all__ = ["get_requisition_df"]


def get_requisition_df(
    extra_panels: list[RequisitionPanel] | None = None,
    exclude_item_types: list[str] | None = None,
    keep_as_uuid: bool | None = None,
) -> pd.DataFrame:
    records: list[tuple[str, str]] = []
    extra_panels: list = extra_panels or []
    exclude_item_types: list = exclude_item_types or []
    requisition_model_cls = django_apps.get_model(settings.SUBJECT_REQUISITION_MODEL)
    df = read_frame(
        requisition_model_cls.objects.values(
            "id",
            "subject_identifier",
            "subject_visit",
            "subject_visit__visit_code",
            "subject_visit__visit_code_sequence",
            "subject_visit__report_datetime",
            "requisition_identifier",
            "report_datetime",
            "drawn_datetime",
            "panel__name",
        )
        .filter(drawn_datetime__isnull=False)
        .exclude(item_type__in=exclude_item_types),
        verbose=False,
    ).rename(
        columns={
            "id": "requisition",
            "report_datetime": "requisition_datetime",
            "subject_visit_id": "subject_visit",
            "subject_visit__visit_code": "visit_code",
            "subject_visit__visit_code_sequence": "visit_code_sequence",
            "subject_visit__report_datetime": "visit_datetime",
            "panel__name": "panel_name",
        }
    )
    df["visit_datetime"] = pd.to_datetime(df["visit_datetime"], utc=True).dt.normalize()
    df["requisition_datetime"] = pd.to_datetime(
        df["requisition_datetime"], utc=True
    ).dt.normalize()
    df["drawn_datetime"] = pd.to_datetime(df["drawn_datetime"], utc=True).dt.normalize()
    df["subject_identifier"] = df["subject_identifier"].astype("string").fillna(pd.NA)
    df["requisition_identifier"] = df["requisition_identifier"].astype("string").fillna(pd.NA)
    if not keep_as_uuid:
        df["requisition"] = df["requisition"].astype("string").fillna(pd.NA)
    df["subject_visit"] = df["subject_visit"].astype("string").fillna(pd.NA)
    df["visit_code"] = df["visit_code"].astype("string").fillna(pd.NA)
    df["panel_name"] = df["panel_name"].astype("string").fillna(pd.NA)

    df = convert_visit_code_to_float(df)

    for lab_profile in site_labs.lab_profiles.values():
        for panel in lab_profile.panels.values():
            for utestid in panel.flatten_utestids():
                records.append((utestid, panel.name))  # noqa: PERF401
    for panel in extra_panels:
        for utestid in panel.flatten_utestids():
            records.append((utestid, panel.name))  # noqa: PERF401
    df_utestid = pd.DataFrame(records, columns=["utestid", "panel_name"]).drop_duplicates()
    if not df_utestid.utestid.is_unique:
        raise ValueError("Utestid column must be unique.")
    df_utestid["utestid"] = df_utestid["utestid"].astype("string").fillna(pd.NA)
    df_utestid["panel_name"] = df_utestid["panel_name"].astype("string").fillna(pd.NA)
    df = df.merge(df_utestid, on="panel_name", how="left")
    return (
        df.sort_values("visit_code_sequence")
        .drop_duplicates(
            subset=["subject_identifier", "visit_code", "drawn_datetime", "utestid"],
            keep="first",
        )
        .reset_index(drop=True)
    )
