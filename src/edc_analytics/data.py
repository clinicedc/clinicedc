from datetime import datetime
from pathlib import Path

import pandas as pd


class Data:

    def __init__(
        self,
        label: str,
        table_df: pd.DataFrame,
        data_df: pd.DataFrame,
        filename_prefix: str,
        folder: str | None = None,
    ):
        self.label = label
        self.table_df = table_df
        self.data_df = data_df
        self.filename_prefix = filename_prefix
        self.folder = folder or "~/"

    def __repr__(self):
        return f"Data({self.label}) <obs={len(self.data_df)}>"

    def to_csv(
        self, folder: str | None = None, filename: str | None = None, cols: int | None = None
    ):
        folder = folder or self.folder
        cols = cols or 5
        datestamp = datetime.now().strftime("%Y%m%d%H%M")
        filename = filename or f"{self.filename_prefix}_table_{self.label}_{datestamp}.csv"
        path = Path(folder) / filename
        self.table_df.iloc[:, :cols].to_csv(
            path_or_buf=path, encoding="utf-8", index=0, sep="|"
        )
