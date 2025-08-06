from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
from django.apps import apps as django_apps
from django.db.models import Count
from django_pandas.io import read_frame

if TYPE_CHECKING:

    from ..models import Location


def get_stock_for_location_df(location: Location) -> pd.DataFrame:
    """Returns a dataframe of all stock records for this
    location.
    """
    stock_model_cls = django_apps.get_model("edc_pharmacy.Stock")
    qs_stock = (
        stock_model_cls.objects.values(
            "code",
            "unit_qty_in",
            "unit_qty_out",
            "confirmation",
            "allocation__registered_subject__subject_identifier",
            "stocktransferitem",
            "confirmationatsiteitem",
            "dispenseitem",
            "location__name",
        )
        .filter(location=location, qty=1)
        .annotate(count=Count("allocation__registered_subject__subject_identifier"))
    )
    df_stock = read_frame(qs_stock).rename(
        columns={
            "allocation__registered_subject__subject_identifier": "subject_identifier",
            "location__name": "location",
            # "confirmationatsiteitem": "confirmed_at_site",
            "count": "stock_qty",
        }
    )
    df_stock = df_stock.fillna(pd.NA)
    df_stock["unit_qty_bal"] = df_stock["unit_qty_in"] - df_stock["unit_qty_out"]
    df_stock["confirmed"] = False
    df_stock.loc[~df_stock["confirmation"].isna(), "confirmed"] = True
    df_stock["transferred"] = False
    df_stock.loc[~df_stock["stocktransferitem"].isna(), "transferred"] = True
    df_stock["confirmed_at_site"] = False
    df_stock.loc[~df_stock["confirmationatsiteitem"].isna(), "confirmed_at_site"] = True
    df_stock["dispensed"] = False
    df_stock.loc[~df_stock["dispenseitem"].isna(), "dispensed"] = True
    df_stock = df_stock.reset_index(drop=True)
    return df_stock
