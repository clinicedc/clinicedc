import pandas as pd

from ..default_columns import default_columns
from ..table import Row, Table


class BpTable(Table):

    sys_col_name = "sys_blood_pressure_avg"
    dia_col_name = "dia_blood_pressure_avg"

    def __init__(self, main_df: pd.DataFrame = None):
        super().__init__(
            main_df=main_df,
            label="Blood pressure at baseline (mmHg)",
            columns=default_columns,
            show_ncol_perc=True,
        )

    def build_table_df(self):
        self.table_df.loc[0] = self.row_zero.values()
        i = 1
        for key, dfx in self.get_dfs().items():
            self.table_df.loc[i] = Row(
                dfx, self.main_df, label="", statistic=key, columns=self.columns
            ).values()
            i += 1
        self.table_df.loc[i + 1] = Row(
            self.main_df,
            self.main_df,
            label="",
            statistic="Systolic - median (IQR)",
            iqr_col=self.sys_col_name,
            columns=self.columns,
        ).values()
        self.table_df.loc[i + 2] = Row(
            self.main_df,
            self.main_df,
            label="",
            statistic="Diastolic - median (IQR)",
            iqr_col=self.dia_col_name,
            columns=self.columns,
        ).values()

    def get_dfs(self) -> dict[str, pd.DataFrame]:
        """Returns a dictionary of dataframes"""
        dfs = {}
        df_tmp = self.main_df.copy()
        severe_htn_cond = (df_tmp["sys_blood_pressure_avg"] >= 180) | (
            df_tmp["dia_blood_pressure_avg"] >= 110
        )
        severe_htn_df = df_tmp[severe_htn_cond]
        dfs.update({"Severe hypertension (>=180/110)": severe_htn_df})
        df_tmp.drop(severe_htn_df.index, inplace=True)

        htn_cond = (df_tmp["sys_blood_pressure_avg"] >= 140) | (
            df_tmp["dia_blood_pressure_avg"] >= 90
        )
        htn_df = df_tmp[htn_cond]
        dfs.update({"Hypertension (>=140/90)": htn_df})
        df_tmp.drop(htn_df.index, inplace=True)

        pre_htn_cond = (df_tmp["sys_blood_pressure_avg"] >= 120) | (
            df_tmp["dia_blood_pressure_avg"] >= 80
        )
        pre_htn_df = df_tmp[pre_htn_cond]
        dfs.update({"Pre-hypertension (<140/90)": pre_htn_df})
        df_tmp.drop(pre_htn_df.index, inplace=True)

        normal_cond = (df_tmp["sys_blood_pressure_avg"] >= 90) | (
            df_tmp["dia_blood_pressure_avg"] >= 60
        )
        normal_df = df_tmp[normal_cond]
        dfs.update({"Normal (<120/80)": normal_df})
        df_tmp.drop(normal_df.index, inplace=True)

        low_cond = (df_tmp["sys_blood_pressure_avg"] >= 0) | (
            df_tmp["dia_blood_pressure_avg"] >= 0
        )
        low_df = df_tmp[low_cond]
        dfs.update({"Low (<90/60)": low_df})
        df_tmp.drop(low_df.index, inplace=True)
        dfs = dict(reversed(list(dfs.items())))
        return dfs
