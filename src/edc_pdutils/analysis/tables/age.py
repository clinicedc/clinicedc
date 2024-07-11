import pandas as pd

from edc_pdutils.analysis import Row, Table, default_columns


class AgeTableMedian(Table):
    def __init__(self, main_df):
        super().__init__(main_df, label="", columns=default_columns, show_range=True)

    @property
    def row_zero(self) -> Row:
        if not self._row_zero:
            self._row_zero = Row(
                self.main_df,
                self.main_df,
                label=self.label,
                statistic="Median (range)",
                columns=self.columns,
                iqr_col="age_in_years",
            )
        return self._row_zero


class AgeTable(Table):
    def __init__(self, main_df: pd.DataFrame = None):
        super().__init__(
            main_df=main_df, label="Age (years)", columns=default_columns, show_ncol_perc=True
        )

    def build_table_df(self):
        super().build_table_df()
        i = 1
        for key, dfx in self.get_dfs().items():
            self.table_df.loc[i] = Row(
                dfx, self.main_df, label="", statistic=key, columns=self.columns
            ).values()
            i += 1
        tbl = AgeTableMedian(main_df=self.main_df)
        self.table_df = pd.concat([self.table_df, tbl.table_df], ignore_index=True)

    def get_dfs(self) -> dict[str, pd.DataFrame]:
        dfs = {}

        bin1 = (self.main_df["age_in_years"] >= 18) & (self.main_df["age_in_years"] < 35)
        bin2 = (self.main_df["age_in_years"] >= 35) & (self.main_df["age_in_years"] < 50)
        bin3 = (self.main_df["age_in_years"] >= 50) & (self.main_df["age_in_years"] < 65)
        bin4 = self.main_df["age_in_years"] >= 65

        dfs.update({"18-34": self.main_df[bin1]})
        dfs.update({"35-49": self.main_df[bin2]})
        dfs.update({"50-64": self.main_df[bin3]})
        dfs.update({"65 and older": self.main_df[bin4]})

        cond = self.main_df["age_in_years"].isna()
        if len(self.main_df[cond]) > 0:
            dfs.update({"not recorded": self.main_df[cond]})
        return dfs

    def check(self, total: int):
        return self.table_df["tot"][1:5].sum() == total
