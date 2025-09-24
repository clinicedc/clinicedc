import pandas as pd

from edc_constants.constants import FEMALE, MALE

from ..constants import MEDIAN_RANGE, N_ONLY, N_WITH_COL_PROP, N_WITH_ROW_PROP
from ..row import RowDefinition, RowDefinitions
from ..table import Table


class AgeTable(Table):

    col_a = FEMALE
    col_b = MALE
    column_name = "gender"

    def __init__(self, main_df: pd.DataFrame = None):
        super().__init__(colname="age_in_years", main_df=main_df, title="Age (years)")

    @property
    def row_definitions(self) -> RowDefinitions:
        df_tmp = self.main_df.copy()
        row_defs = RowDefinitions(reverse_rows=False)
        row0 = RowDefinition(
            title=self.title,
            label=self.default_sublabel,
            condition=(df_tmp[self.column_name].notna()),
            columns={
                self.col_a: (N_ONLY, 2),
                self.col_b: (N_ONLY, 2),
                "All": (N_ONLY, 2),
            },
            drop=False,
        )
        row_defs.add(row0)
        columns = {
            self.col_a: (N_WITH_COL_PROP, 2),
            self.col_b: (N_WITH_COL_PROP, 2),
            "All": (N_WITH_ROW_PROP, 2),
        }
        bin1 = (df_tmp[self.colname] >= 18) & (df_tmp[self.colname] < 35)
        bin2 = (df_tmp[self.colname] >= 35) & (df_tmp[self.colname] < 50)
        bin3 = (df_tmp[self.colname] >= 50) & (df_tmp[self.colname] < 65)
        bin4 = df_tmp[self.colname] >= 65
        row_defs.add(RowDefinition(label="18-34", condition=bin1, columns=columns, drop=False))
        row_defs.add(RowDefinition(label="35-49", condition=bin2, columns=columns, drop=False))
        row_defs.add(RowDefinition(label="50-64", condition=bin3, columns=columns, drop=False))
        row_defs.add(
            RowDefinition(label="65 and older", condition=bin4, columns=columns, drop=False)
        )
        if len(df_tmp[df_tmp[self.colname].isna()]) > 0:
            row_defs.add(
                RowDefinition(
                    colname="age_in_years",
                    label="not recorded",
                    condition=(df_tmp[self.colname].isna()),
                    columns=columns,
                    drop=False,
                )
            )
        columns = {
            self.col_a: (MEDIAN_RANGE, 2),
            self.col_b: (MEDIAN_RANGE, 2),
            "All": (MEDIAN_RANGE, 2),
        }
        row_defs.add(
            RowDefinition(
                colname="age_in_years",
                label="Median (range)",
                condition=(self.main_df[self.colname].notna()),
                columns=columns,
            )
        )
        return row_defs
