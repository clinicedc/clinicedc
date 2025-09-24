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


class BmiTable(Table):

    colname = "calculated_bmi_value"

    def __init__(self, main_df: pd.DataFrame = None):
        super().__init__(
            colname="calculated_bmi_value",
            main_df=main_df,
            title="BMI categories (kg/m2)",
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
        row_defs.add(
            RowDefinition(
                colname="calculated_bmi_value",
                label="Less than 18.5",
                condition=(df_tmp[self.colname] < 18.5),
                columns=columns,
                drop=False,
            )
        )
        row_defs.add(
            RowDefinition(
                colname="calculated_bmi_value",
                label="18.5-24.9",
                condition=(df_tmp[self.colname] >= 18.5) & (df_tmp[self.colname] < 25.0),
                columns=columns,
                drop=False,
            )
        )
        row_defs.add(
            RowDefinition(
                colname="calculated_bmi_value",
                label="25.0-29.9",
                condition=(df_tmp[self.colname] >= 25.0) & (df_tmp[self.colname] < 30.0),
                columns=columns,
                drop=False,
            )
        )
        row_defs.add(
            RowDefinition(
                colname="calculated_bmi_value",
                label="30.0-39.9",
                condition=(df_tmp[self.colname] >= 30.0) & (df_tmp[self.colname] < 40.0),
                columns=columns,
                drop=False,
            )
        )
        row_defs.add(
            RowDefinition(
                colname="calculated_bmi_value",
                label="40 or above",
                condition=(df_tmp[self.colname] >= 40.0),
                columns=columns,
                drop=False,
            )
        )
        cond = df_tmp[self.colname].isna()
        if len(df_tmp[cond]) > 0:
            row_defs.add(
                RowDefinition(
                    colname="calculated_bmi_value",
                    label="not measured",
                    condition=cond,
                    columns=columns,
                    drop=False,
                )
            )
        row_defs.add(
            RowDefinition(
                colname="calculated_bmi_value",
                label="Median (IQR)",
                condition=(df_tmp["gender"].notna()),
                columns={
                    FEMALE: (MEDIAN_IQR, 2),
                    MALE: (MEDIAN_IQR, 2),
                    "All": (MEDIAN_IQR, 2),
                },
                drop=False,
            )
        )
        row_defs.add(
            RowDefinition(
                colname="calculated_bmi_value",
                label="Median (range)",
                condition=(df_tmp["gender"].notna()),
                columns={
                    FEMALE: (MEDIAN_RANGE, 2),
                    MALE: (MEDIAN_RANGE, 2),
                    "All": (MEDIAN_RANGE, 2),
                },
                drop=False,
            )
        )
        return row_defs
