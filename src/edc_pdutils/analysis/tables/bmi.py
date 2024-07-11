import pandas as pd

from edc_pdutils.analysis import Row, Table, default_columns


class BmiMedianTable(Table):
    def __init__(self, main_df: pd.DataFrame = None, colname: str = None):
        self.colname = colname
        super().__init__(
            main_df=main_df,
            label="",
            columns=default_columns,
            show_ncol_perc=True,
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
                iqr_col=self.colname,
            )
        return self._row_zero


class BmiTable(Table):

    colname = "calculated_bmi_value"

    def __init__(self, main_df: pd.DataFrame = None):
        super().__init__(
            main_df=main_df,
            label="BMI categories (kg/m2)",
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

        # concat a 'missing' row if any are missing
        median_tbl = BmiMedianTable(self.main_df, colname=self.colname)
        self.table_df = pd.concat([self.table_df, median_tbl.table_df], ignore_index=True)

    def get_dfs(self) -> dict[str, pd.DataFrame]:
        """Returns a dictionary of dataframes"""
        dfs = {}

        dfs.update({"Less than 18.5": self.main_df[(self.main_df[self.colname] < 18.5)]})

        cond = (self.main_df[self.colname] >= 18.5) & (self.main_df[self.colname] < 25.0)
        dfs.update({"18.5-24.9": self.main_df[cond]})

        cond = (self.main_df[self.colname] >= 25.0) & (self.main_df[self.colname] < 30.0)
        dfs.update({"18.5-24.9": self.main_df[cond]})

        cond = (self.main_df[self.colname] >= 25.0) & (self.main_df[self.colname] < 40.0)
        dfs.update({"25.0-39.9": self.main_df[cond]})

        cond = self.main_df[self.colname] >= 40.0
        dfs.update({"40 or above": self.main_df[cond]})

        cond = self.main_df[self.colname].isna()
        if len(self.main_df[cond]) > 0:
            dfs.update({"not measured": self.main_df[cond]})
        return dfs
