from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
from django.apps import apps as django_apps
from django.db.models import Count
from django_pandas.io import read_frame

if TYPE_CHECKING:

    from ...models import StockRequest


def get_instock_and_nostock_data(
    stock_request: StockRequest, df: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
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
        df_subject = df.copy()
        df_subject["code"] = None
        df = df.merge(df_stock, on="subject_identifier", how="left")
        for subject_identifier in df.subject_identifier.unique():
            qty_needed = stock_request.containers_per_subject - len(
                df[df.subject_identifier == subject_identifier]
            )
            if qty_needed > 0:
                df1 = df_subject[df_subject.subject_identifier == subject_identifier].copy()
                df1["code"] = None
                df1 = df1.loc[df1.index.repeat(qty_needed)]
                df = pd.concat([df, df1])
                df.reset_index(drop=True, inplace=True)
    else:
        df["code"] = None
    df["stock_qty"] = 0.0
    df = df.reset_index(drop=True)

    df_instock = df[~df.code.isna()]
    df_instock = df_instock.reset_index(drop=True)
    df_instock = df_instock.sort_values(by=["subject_identifier"])

    df_nostock = df[df.code.isna()]
    df_nostock = df_nostock.reset_index(drop=True)
    df_nostock = df_nostock.sort_values(by=["subject_identifier"])
    df_nostock["code"] = df_nostock["code"].fillna("---")
    return df_instock, df_nostock


__all__ = ["get_instock_and_nostock_data"]
