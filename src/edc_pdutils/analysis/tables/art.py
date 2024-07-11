import pandas as pd

from edc_pdutils.analysis import Row, Table, default_columns


class ArtTable(Table):
    def __init__(self, main_df: pd.DataFrame = None):
        self.n_sublabel = "n"
        super().__init__(
            main_df=main_df,
            label="HIV Care",
            columns=default_columns,
            show_ncol_perc=True,
        )

    @property
    def cond_art_stable(self) -> tuple:
        return (
            (self.main_df["on_rx_stable"] == "Yes")
            & (self.main_df["vl_undetectable"] == "Yes")
            & (self.main_df["art_six_months"] == "Yes")
        )

    @property
    def row_zero(self) -> Row:
        if not self._row_zero:
            self._row_zero = Row(
                self.main_df,
                self.main_df,
                label=self.label,
                statistic=self.n_sublabel,
                columns=self.columns,
                use_rowperc=True,
            )
        return self._row_zero

    def build_table_df(self):
        super().build_table_df()
        i = 1
        for key, df in self.get_dfs().items():
            if len(df) > 0:
                row = Row(
                    df,
                    self.main_df,
                    label="",
                    statistic=key,
                    columns=self.columns,
                )
                self.table_df.loc[i] = row.values()
                i += 1

    def get_dfs(self) -> dict[str, pd.DataFrame]:
        dfs = {}
        df_tmp = self.main_df.copy()
        df_stable = df_tmp[self.cond_art_stable]
        dfs.update({"Stable on ART (6m)": df_stable})

        df_tmp.drop(df_stable.index, inplace=True)

        # look for anyone that is not stable by these three values
        cond = (
            (df_tmp["on_rx_stable"] == "Yes")
            | (df_tmp["vl_undetectable"] == "Yes")
            | (df_tmp["art_six_months"] == "Yes")
        )
        df_stable_ish = df_tmp[cond]
        dfs.update({"Other stable (`VL` or `on ART` or `stable 6m`)": df_stable_ish})

        df_tmp.drop(df_stable_ish.index, inplace=True)

        cond = (
            (df_tmp["on_rx_stable"].isna())
            & (df_tmp["vl_undetectable"].isna())
            & (df_tmp["art_six_months"].isna())
        )
        missing_df = df_tmp[cond]
        df_tmp.drop(missing_df.index, inplace=True)
        dfs.update({"Other": df_tmp})
        dfs.update({"Not recorded ": missing_df})

        return dfs
