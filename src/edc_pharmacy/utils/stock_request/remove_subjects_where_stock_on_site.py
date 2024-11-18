from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.db.models import Count
from django_pandas.io import read_frame

if TYPE_CHECKING:
    import pandas as pd

    from ...models import StockRequest


def remove_subjects_where_stock_on_site(stock_request: StockRequest, df: pd.DataFrame):
    stock_model_cls = django_apps.get_model("edc_pharmacy.Stock")
    qs_stock = (
        stock_model_cls.objects.values(
            "allocation__registered_subject__subject_identifier", "code"
        )
        .filter(location=stock_request.location, qty=1)
        .annotate(count=Count("allocation__registered_subject__subject_identifier"))
    )
    df_stock = read_frame(qs_stock)
    df_stock = df_stock.rename(
        columns={
            "allocation__registered_subject__subject_identifier": "subject_identifier",
            "count": "stock_qty",
        }
    )
    if not df.empty and not df_stock.empty:
        df = df.merge(df_stock, on="subject_identifier", how="left")
    else:
        df["code"] = None
    df["stock_qty"] = 0.0
    df = df.reset_index(drop=True)
    return df
