import pandas as pd

from edc_pdutils.analysis import Row, Table, default_columns


class FbgOgttTable(Table):
    def __init__(self, main_df: pd.DataFrame = None):
        super().__init__(
            main_df=main_df,
            label="OGTT & FBG (mmol/L) categories",
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
        """Returns a dictionary of dataframes"""
        dfs = {}

        df_tmp = self.main_df.copy()

        cond = (
            (self.main_df["ogtt"] >= 11.1)
            & (self.main_df["fbg"] >= 7.0)
            & (self.main_df["ogtt"].notna())
        )
        df = df_tmp[cond]
        dfs.update({"OGTT>=11.1 and FBG>=7.0": df})
        df_tmp.drop(df.index, inplace=True)

        cond = (df_tmp["ogtt"] >= 11.1) | (df_tmp["fbg"] >= 7.0) & (df_tmp["ogtt"].notna())
        df = df_tmp[cond]
        dfs.update({"OGTT>=11.1 or FBG>=7.0": df})
        df_tmp.drop(df.index, inplace=True)

        cond = ~((df_tmp["ogtt"] >= 11.1) | (df_tmp["fbg"] >= 7.0)) & (df_tmp["ogtt"].notna())
        dfs.update({"other": df_tmp[cond]})

        cond = (df_tmp["fbg"].notna()) & (df_tmp["ogtt"].isna())
        dfs.update({"OGTT not done": df_tmp[cond]})

        return dfs
