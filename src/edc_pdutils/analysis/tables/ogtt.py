import pandas as pd

from edc_pdutils.analysis import Row, Table, default_columns


class OgttTable(Table):
    def __init__(self, main_df: pd.DataFrame = None):
        super().__init__(
            main_df=main_df,
            label="OGTT (mmol/L) categories",
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

        dfs.update({"<7.7": self.main_df[(self.main_df["ogtt"] < 7.8)]})

        cond = (self.main_df["ogtt"] >= 7.8) & (self.main_df["ogtt"] < 11.1)
        dfs.update({"7.8-11.1": self.main_df[cond]})

        dfs.update({"11.1 and above": self.main_df[(self.main_df["ogtt"] >= 11.1)]})

        dfs.update({"not done": self.main_df[(self.main_df["ogtt"].isna())]})

        return dfs

    def check(self, total: int):
        return total == self.table_df["tot"][1:5].sum()
