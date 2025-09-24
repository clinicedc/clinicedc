import pandas as pd

from edc_constants.constants import FEMALE, MALE

from ..constants import MEAN_95CI, N_ONLY, N_WITH_COL_PROP, N_WITH_ROW_PROP
from ..row import RowDefinition, RowDefinitions
from ..table import Table


class HbA1cTable(Table):
    def __init__(self, main_df: pd.DataFrame = None):
        super().__init__(
            colname="hba1c_value",
            main_df=main_df,
            title="HbA1C (%) categories",
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
            FEMALE: (MEAN_95CI, 2),
            MALE: (MEAN_95CI, 2),
            "All": (MEAN_95CI, 2),
        }
        row_mean = RowDefinition(
            colname=self.colname,
            label="Mean (95% CI)",
            condition=(self.main_df[self.colname].notna()),
            columns=columns,
            drop=False,
        )

        columns = {
            FEMALE: (N_WITH_COL_PROP, 2),
            MALE: (N_WITH_COL_PROP, 2),
            "All": (N_WITH_ROW_PROP, 2),
        }
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="<6.0",
                condition=(self.main_df[self.colname] < 6.0),
                columns=columns,
                drop=False,
            )
        )
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="≥6.0 and ≤6.4",
                condition=(
                    (self.main_df[self.colname] >= 6.0) & (self.main_df[self.colname] <= 6.4)
                ),
                columns=columns,
                drop=False,
            )
        )
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label=">6.4",
                condition=(self.main_df[self.colname] > 6.4),
                columns=columns,
                drop=False,
            )
        )
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="not measured",
                condition=(self.main_df[self.colname].isna()),
                columns=columns,
                drop=False,
            )
        )
        row_defs.add(row_mean)
        return row_defs
