from __future__ import annotations

import pandas as pd

from .stock_for_subjects import stock_for_subjects_df


def no_stock_for_subjects_df() -> pd.DataFrame:
    return stock_for_subjects_df().query("codes.isna()").reset_index(drop=True)
