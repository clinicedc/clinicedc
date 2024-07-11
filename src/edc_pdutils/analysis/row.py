import numpy as np
import pandas as pd

from edc_pdutils.analysis import default_columns


class SubjectRow:
    def __init__(
        self, gender: str, dfx: pd.DataFrame, main_df: pd.DataFrame, iqr_col: str | None = None
    ):
        self.num = dfx.loc[dfx["gender"] == gender]["gender"].count()
        self.total = len(main_df.loc[main_df["gender"] == gender])
        self.colperc = self.num / self.total
        self.rowperc = self.num / len(main_df)
        if iqr_col:
            self.q25, self.q50, self.q75 = dfx.loc[dfx["gender"] == gender][iqr_col].quantile(
                [0.25, 0.50, 0.75]
            )
        else:
            self.q25, self.q50, self.q75 = np.nan, np.nan, np.nan
        self.min = dfx.loc[dfx["gender"] == gender][iqr_col].min() if iqr_col else np.nan
        self.max = dfx.loc[dfx["gender"] == gender][iqr_col].max() if iqr_col else np.nan


class MaleRow(SubjectRow):
    def __init__(self, dfx: pd.DataFrame, main_df: pd.DataFrame, iqr_col: str | None = None):
        super().__init__("Male", dfx, main_df, iqr_col)


class FemaleRow(SubjectRow):
    def __init__(self, dfx: pd.DataFrame, main_df: pd.DataFrame, iqr_col: str | None = None):
        super().__init__("Female", dfx, main_df, iqr_col)


class Row:
    def __init__(
        self,
        dfx: pd.DataFrame,
        main_df: pd.DataFrame,
        label: str | None = None,
        statistic: str | None = None,
        iqr_col: str | None = None,
        columns: list[str] = None,
        n_sublabel: str | None = None,
        use_rowperc: bool = False,
    ):
        self.columns = columns or default_columns
        self.n_sublabel = n_sublabel or "n"
        self.use_rowperc = use_rowperc
        self.m = MaleRow(dfx, main_df, iqr_col)
        self.f = FemaleRow(dfx, main_df, iqr_col)
        self.total = len(main_df)
        self.subtotal = len(dfx)
        self.min = main_df[iqr_col].min() if iqr_col else np.nan
        self.max = main_df[iqr_col].max() if iqr_col else np.nan
        self.n_sublabel = n_sublabel
        if iqr_col:
            self.q25, self.q50, self.q75 = main_df[iqr_col].quantile([0.25, 0.50, 0.75])
        else:
            self.q25, self.q50, self.q75 = np.nan, np.nan, np.nan
        self.label = label or ""
        self.statistic = statistic
        self.df = pd.DataFrame(columns=self.columns)

    def values(self):
        if self.statistic == self.n_sublabel:
            return [
                self.label,
                self.statistic,
                "",
                "",
                "",
                self.f.num,
                self.f.rowperc if self.use_rowperc else self.f.colperc,
                self.f.q25,
                self.f.q50,
                self.f.q75,
                self.f.min,
                self.f.max,
                self.m.num,
                self.m.rowperc if self.use_rowperc else self.m.colperc,
                self.m.q25,
                self.m.q50,
                self.m.q75,
                self.m.min,
                self.m.max,
                self.q25,
                self.q50,
                self.q75,
                self.min,
                self.max,
                self.total,
            ]
        return [
            self.label,
            self.statistic,
            "",
            "",
            "",
            self.f.num,
            self.f.rowperc if self.use_rowperc else self.f.colperc,
            self.f.q25,
            self.f.q50,
            self.f.q75,
            self.f.min,
            self.f.max,
            self.m.num,
            self.m.rowperc if self.use_rowperc else self.m.colperc,
            self.m.q25,
            self.m.q50,
            self.m.q75,
            self.m.min,
            self.m.max,
            self.q25,
            self.q50,
            self.q75,
            self.min,
            self.max,
            self.subtotal,
        ]
