import pandas as pd

from edc_constants.constants import FEMALE, MALE

from ..constants import N_ONLY, N_WITH_COL_PROP, N_WITH_ROW_PROP
from ..row import RowDefinition, RowDefinitions
from ..table import Table


class BpTable(Table):

    sys_col_name = "sys_blood_pressure_avg"
    dia_col_name = "dia_blood_pressure_avg"

    def __init__(self, main_df: pd.DataFrame = None):
        super().__init__(
            colname="",
            main_df=main_df,
            title="Blood pressure at baseline (mmHg)",
        )
        self.table_df = self.table_df.reindex(index=self.table_df.index[::-1])

    @property
    def row_definitions(self) -> RowDefinitions:
        df_tmp = self.main_df.copy()
        row_defs = RowDefinitions(reverse_rows=True)
        row0 = RowDefinition(
            title=self.title,
            label=self.default_sublabel,
            condition=(df_tmp["gender"].notna()),
            columns={
                FEMALE: (N_ONLY, 2),
                MALE: (N_ONLY, 2),
                "All": (N_ONLY, 2),
            },
            drop=False,
        )
        row_defs.add(row0)
        columns = {
            FEMALE: (N_WITH_COL_PROP, 2),
            MALE: (N_WITH_COL_PROP, 2),
            "All": (N_WITH_ROW_PROP, 2),
        }
        row_defs.add(
            RowDefinition(
                label="Severe hypertension (>=180/110)",
                condition=(
                    (df_tmp[self.sys_col_name] >= 180) | (df_tmp[self.dia_col_name] >= 110)
                ),
                columns=columns,
                drop=True,
            )
        )
        row_defs.add(
            RowDefinition(
                label="Hypertension (>=140/90)",
                condition=(
                    (df_tmp[self.sys_col_name] >= 140) | (df_tmp[self.dia_col_name] >= 90)
                ),
                columns=columns,
                drop=True,
            )
        )
        row_defs.add(
            RowDefinition(
                label="Pre-hypertension (<140/90)",
                condition=(
                    (df_tmp[self.sys_col_name] >= 120) | (df_tmp[self.dia_col_name] >= 80)
                ),
                columns=columns,
                drop=True,
            )
        )
        row_defs.add(
            RowDefinition(
                label="Normal (<120/80)",
                condition=(
                    (df_tmp[self.sys_col_name] >= 90) | (df_tmp[self.dia_col_name] >= 60)
                ),
                columns=columns,
                drop=True,
            )
        )
        row_defs.add(
            RowDefinition(
                label="Low (<90/60)",
                condition=(
                    (df_tmp[self.sys_col_name] >= 0) | (df_tmp[self.dia_col_name] >= 0)
                ),
                columns=columns,
                drop=True,
            )
        )
        row_defs.add(
            RowDefinition(
                label="not measured",
                condition=(
                    (df_tmp[self.sys_col_name].isna()) & (df_tmp[self.dia_col_name].isna())
                ),
                columns=columns,
                drop=True,
            )
        )
        return row_defs
