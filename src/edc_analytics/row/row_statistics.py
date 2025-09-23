import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype

from ..constants import COUNT_COLUMN, N_ONLY
from ..styler import Styler


class RowStatistics:
    """A class that calculates descriptive statistics for an
    indictor.
    """

    def __init__(
        self,
        colname: str = None,
        df_numerator: pd.DataFrame = None,
        df_denominator: pd.DataFrame = None,
        df_all: pd.DataFrame = None,
        coltotal: float | int | None = None,
        style: str | None = None,
        places: int | None = None,
    ):
        self.places = 2 if places is None else places
        self.style = style or N_ONLY

        # counts (6 columns)
        self.count = 0.0 if df_numerator.empty else len(df_numerator)
        self.total = len(df_all)
        self.coltotal = coltotal or len(df_denominator)
        self.rowtotal = self.count  # rowtotal or len(df_denominator)
        self.colprop = self.count / self.coltotal if self.count else 0.0
        self.rowprop = self.count / self.total if self.count else 0.0

        # numeric stats (9 columns)
        if colname and not df_numerator.empty and is_numeric_dtype(df_numerator[colname]):
            stats = df_numerator[colname].describe()
            self.mean = stats.loc["mean"]
            self.sd = stats.loc["std"]
            self.min = stats.loc["min"]
            self.max = stats.loc["max"]
            self.q25, self.q50, self.q75 = df_numerator[colname].quantile([0.25, 0.50, 0.75])
            stats = df_numerator[colname].agg(["mean", "sem"])
            self.ci95l = stats.loc["mean"] - 1.96 * stats.loc["sem"]
            self.ci95h = stats.loc["mean"] + 1.96 * stats.loc["sem"]
        else:
            (
                self.mean,
                self.sd,
                self.min,
                self.max,
                self.q25,
                self.q50,
                self.q75,
                self.ci95l,
                self.ci95h,
            ) = [np.nan] * 9

    def values_list(self) -> list:
        return list(self.as_dict().values())

    def labels(self) -> list:
        return list(self.as_dict().keys())

    def as_dict(self):
        return {
            COUNT_COLUMN: self.count,
            "coltotal": self.coltotal,
            "rowtotal": self.rowtotal,
            "total": self.total,
            "colprop": self.colprop,
            "rowprop": self.rowprop,
            "mean": self.mean,
            "sd": self.sd,
            "min": self.min,
            "max": self.max,
            "q25": self.q25,
            "q50": self.q50,
            "q75": self.q75,
            "ci95l": self.ci95l,
            "ci95h": self.ci95h,
        }

    def formatted_cell(self) -> str:
        return Styler(style=self.style, statistics=self, places=self.places).value

    def row(self):
        return [self.formatted_cell()] + self.values_list()
