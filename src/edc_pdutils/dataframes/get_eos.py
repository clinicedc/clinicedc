import pandas as pd
from django.apps import apps as django_apps
from django_pandas.io import read_frame


def get_eos(
    model: str,
    subject_identifiers: list[str] | None = None,
    value_cols: list[str] | None = None,
) -> pd.DataFrame:
    model_cls = django_apps.get_model(model)
    value_cols = ["subject_identifier", "offstudy_datetime", "offstudy_reason"]
    if subject_identifiers:
        qs = model_cls.objects.values(*value_cols).filter(
            subject_identifier__in=subject_identifiers
        )
    else:
        qs = model_cls.objects.values(*value_cols).all()
    df = read_frame(qs)
    df["offstudy_datetime"] = df["offstudy_datetime"].apply(pd.to_datetime)
    if not df["offstudy_datetime"].empty:
        df["offstudy_datetime"] = df["offstudy_datetime"].dt.floor("d")
    df.sort_values(by=["subject_identifier"])
    df.reset_index(drop=True, inplace=True)
    return df
