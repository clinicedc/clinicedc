import pandas as pd

from edc_constants.constants import FEMALE, MALE

from ..constants import (
    MEDIAN_IQR,
    MEDIAN_RANGE,
    N_ONLY,
    N_WITH_COL_PROP,
    N_WITH_ROW_PROP,
)
from ..row import RowDefinition, RowDefinitions
from ..table import Table


class WaistCircumferenceTable(Table):

    def __init__(self, main_df: pd.DataFrame = None):
        super().__init__(
            colname="waist_circumference",
            main_df=main_df,
            title="Waist circumference (cm)",
        )

    @property
    def row_definitions(self) -> RowDefinitions:
        df_tmp = self.main_df.copy()
        row_defs = RowDefinitions(reverse_rows=False)
        row0 = RowDefinition(
            title=self.title,
            label=self.default_sublabel,
            condition=(df_tmp["gender"].notna()),
            columns={FEMALE: (N_ONLY, 2), MALE: (N_ONLY, 2), "All": (N_ONLY, 2)},
            drop=False,
        )
        row_defs.add(row0)

        columns = {
            FEMALE: (N_WITH_COL_PROP, 2),
            MALE: (N_WITH_COL_PROP, 2),
            "All": (N_WITH_ROW_PROP, 2),
        }

        cond_lt_102 = (
            (self.main_df[self.colname] < 102.0) & (self.main_df["gender"] == "Male")
        ) | ((self.main_df[self.colname] < 88.0) & (self.main_df["gender"] == "Female"))
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="Women<88 / Men<102",
                condition=cond_lt_102,
                columns=columns,
                drop=False,
            )
        )
        cond_gte_102 = (
            (self.main_df[self.colname] >= 102.0) & (self.main_df["gender"] == "Male")
        ) | ((self.main_df[self.colname] >= 88.0) & (self.main_df["gender"] == "Female"))
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="Women>=88 / Men>=102",
                condition=cond_gte_102,
                columns=columns,
                drop=False,
            )
        )
        cond_gte_missing = self.main_df[self.colname].isna()
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="not measured",
                condition=cond_gte_missing,
                columns=columns,
                drop=False,
            )
        )

        columns = {
            FEMALE: (MEDIAN_RANGE, 2),
            MALE: (MEDIAN_RANGE, 2),
            "All": (MEDIAN_RANGE, 2),
        }
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="Median (range)",
                condition=(self.main_df[self.colname].notna()),
                columns=columns,
            )
        )

        columns = {
            FEMALE: (MEDIAN_IQR, 2),
            MALE: (MEDIAN_IQR, 2),
            "All": (MEDIAN_IQR, 2),
        }
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="Median (IQR)",
                condition=(self.main_df[self.colname].notna()),
                columns=columns,
            )
        )
        return row_defs
