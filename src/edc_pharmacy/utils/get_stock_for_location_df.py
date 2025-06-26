from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.db.models import Count
from django_pandas.io import read_frame

if TYPE_CHECKING:
    import pandas as pd

    from ..models import Location


def get_stock_for_location_df(location: Location) -> pd.DataFrame:
    """Returns a dataframe of all stock records for this
    location.
    """
    stock_model_cls = django_apps.get_model("edc_pharmacy.Stock")
    qs_stock = (
        stock_model_cls.objects.values(
            "allocation__registered_subject__subject_identifier", "code", "dispensed"
        )
        .filter(location=location, qty=1)
        .annotate(count=Count("allocation__registered_subject__subject_identifier"))
    )
    df_stock = read_frame(qs_stock).rename(
        columns={
            "allocation__registered_subject__subject_identifier": "subject_identifier",
            "count": "stock_qty",
        }
    )
    df_stock["dispensed"] = df_stock["dispensed"].astype("boolean").fillna(False)
    return df_stock
