from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

from ..get_stock_for_location_df import get_stock_for_location_df

if TYPE_CHECKING:

    from ...models import StockRequest


def get_instock_and_nostock_data(
    stock_request: StockRequest, df_next_scheduled_visits: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:

    df_stock = get_stock_for_location_df(stock_request.location)
    if not df_next_scheduled_visits.empty and not df_stock.empty:
        df_stock = df_next_scheduled_visits.merge(
            df_stock, on="subject_identifier", how="left"
        )
        df_stock["dispensed"] = df_stock["dispensed"].astype("boolean").fillna(False)
        df_stock["stock_qty"] = df_stock["stock_qty"].fillna(0.0)
        for subject_identifier in df_stock.subject_identifier.unique():
            qty_needed = (
                stock_request.containers_per_subject
                - df_stock.loc[
                    (df_stock.subject_identifier == subject_identifier) & ~df_stock.dispensed
                ].shape[0]
            )
            if qty_needed > 0:
                df_stock_needed = df_next_scheduled_visits[
                    df_next_scheduled_visits.subject_identifier == subject_identifier
                ].copy()
                df_stock_needed["code"] = pd.NA
                df_stock_needed = df_stock_needed.loc[df_stock_needed.index.repeat(qty_needed)]
                df_stock = pd.concat([df_stock, df_stock_needed]).reset_index(drop=True)
                df_stock["dispensed"] = df_stock["dispensed"].astype("boolean").fillna(False)
                df_stock["stock_qty"] = 0.0
    else:
        df_stock = df_next_scheduled_visits.copy()
        df_stock["code"] = pd.NA
        df_stock["dispensed"] = False
        df_stock["dispensed"].astype("boolean")
        df_stock["stock_qty"] = 0.0
        df_stock["subject_identifier"] = pd.NA
    df_stock = df_stock.reset_index(drop=True)

    df_instock = (
        df_stock.loc[~(df_stock.code.isna()) & ~df_stock.dispensed]
        .copy()
        .sort_values(by=["subject_identifier"])
        .reset_index(drop=True)
    )
    df_nostock = (
        df_stock.loc[(df_stock.code.isna())]
        .copy()
        .sort_values(by=["subject_identifier"])
        .reset_index(drop=True)
    )
    df_nostock["code"] = df_nostock["code"].fillna(pd.NA)
    return df_instock, df_nostock


__all__ = ["get_instock_and_nostock_data"]
