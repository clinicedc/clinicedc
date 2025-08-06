import pandas as pd
from django.apps import apps as django_apps
from django.contrib.sites.models import Site
from django_pandas.io import read_frame

from ..utils import convert_dates_from_model


def get_eos(
    model: str,
    subject_identifiers: list[str] | None = None,
    normalize: bool | None = None,
    localize: bool | None = None,
    fields: list[str] | None = None,
    all_fields: bool | None = None,
) -> pd.DataFrame:
    normalize = True if normalize is None else normalize
    localize = True if localize is None else localize
    model_cls = django_apps.get_model(model)

    if all_fields:
        fields = [fld.name for fld in model_cls._meta.get_fields()]
    elif not fields:
        fields = ["subject_identifier", "offstudy_datetime", "offstudy_reason", "site"]

    if subject_identifiers:
        qs = model_cls.objects.values(*fields).filter(
            subject_identifier__in=subject_identifiers
        )
    else:
        qs = model_cls.objects.values(*fields).all()

    df = read_frame(qs, verbose=True)

    df = convert_dates_from_model(df, model_cls, normalize=normalize, localize=localize)

    df["site_id"] = df["site"].map({obj.domain: obj.id for obj in Site.objects.all()})
    df = df.drop(columns=["site"])

    df.sort_values(by=["subject_identifier"])
    df = df.reset_index(drop=True)
    return df
