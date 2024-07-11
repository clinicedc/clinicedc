import pandas as pd

from edc_pdutils.analysis import Row, Table, default_columns


class WaistMedian(Table):

    def __init__(self, main_df: pd.DataFrame = None):
        super().__init__(
            main_df=main_df,
            label="",
            columns=default_columns,
        )

    @property
    def row_zero(self) -> Row:
        if not self._row_zero:
            self._row_zero = Row(
                self.main_df,
                self.main_df,
                label=self.label,
                statistic="Median (IQR)",
                columns=self.columns,
                iqr_col="waist_circumference",
            )
        return self._row_zero


class WaistCircumferenceTable(Table):

    def __init__(self, main_df: pd.DataFrame = None):
        super().__init__(
            main_df=main_df,
            label="Waist circumference (cm)",
            columns=default_columns,
            show_ncol_perc=True,
        )

    def build_table_df(self):
        super().build_table_df()
        i = 1
        for key, dfx in self.get_dfs().items():
            self.table_df.loc[i] = Row(
                dfx, self.main_df, label="", statistic=key, columns=self.columns
            ).values()
            i += 1
        tbl = WaistMedian(main_df=self.main_df)
        self.table_df = pd.concat([self.table_df, tbl.table_df], ignore_index=True)

    def get_dfs(self) -> dict[str, pd.DataFrame]:
        dfs = {}
        cond_lt_102 = (
            (self.main_df["waist_circumference"] < 102.0) & (self.main_df["gender"] == "Male")
        ) | (
            (self.main_df["waist_circumference"] < 88.0) & (self.main_df["gender"] == "Female")
        )
        cond_gte_102 = (
            (self.main_df["waist_circumference"] >= 102.0) & (self.main_df["gender"] == "Male")
        ) | (
            (self.main_df["waist_circumference"] >= 88.0)
            & (self.main_df["gender"] == "Female")
        )
        cond_gte_missing = self.main_df["waist_circumference"].isna()

        dfs.update({"Women<88 / Men<102": self.main_df[cond_lt_102]})
        dfs.update({"Women>=88 / Men>=102": self.main_df[cond_gte_102]})
        dfs.update({"not measured": self.main_df[cond_gte_missing]})
        return dfs

    def check(self, total: int):
        return self.table_df["tot"][1:4].sum() == total
