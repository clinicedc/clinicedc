import pandas as pd

from edc_pdutils.analysis import Row, Table, default_columns


class FbgTable(Table):
    def __init__(self, main_df: pd.DataFrame = None):
        super().__init__(
            main_df=main_df,
            label="FBG (mmol/L) categories",
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

    def get_dfs(self) -> dict[str, pd.DataFrame]:
        """Returns a dictionary of dataframes"""
        dfs = {}

        dfs.update({"<6.1": self.main_df[(self.main_df["fbg"] < 6.1)]})

        cond = (self.main_df["fbg"] >= 6.1) & (self.main_df["fbg"] < 7.0)
        dfs.update({"6.1-6.9": self.main_df[cond]})

        dfs.update({"7.0 and above": self.main_df[(self.main_df["fbg"] >= 7.0)]})

        return dfs

    def check(self, total: int):
        return total == self.table_df["tot"][1:4].sum()
