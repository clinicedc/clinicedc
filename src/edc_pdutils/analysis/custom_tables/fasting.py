import pandas as pd

from ..constants import MEDIAN_IQR, N_ONLY, N_WITH_COL_PROP, N_WITH_ROW_PROP
from ..row import RowDefinition, RowDefinitions
from ..table import Table


class FastingFbgTable(Table):
    def __init__(self, main_df: pd.DataFrame = None):
        super().__init__(
            colname="fasting_fbg_hrs", main_df=main_df, title="Fasting duration (hrs)"
        )

    @property
    def row_definitions(self) -> RowDefinitions:
        df_tmp = self.main_df.copy()
        row_defs = RowDefinitions(reverse_rows=False)
        row0 = RowDefinition(
            title=self.title,
            label=self.default_sublabel,
            condition=(df_tmp["gender"].notna()),
            columns={"F": (N_ONLY, 2), "M": (N_ONLY, 2), "All": (N_ONLY, 2)},
            drop=False,
        )
        row_defs.add(row0)
        columns = {
            "F": (MEDIAN_IQR, 2),
            "M": (MEDIAN_IQR, 2),
            "All": (MEDIAN_IQR, 2),
        }
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="FBG fasted (hours), median (IQR)",
                condition=(self.main_df[self.colname].notna()),
                columns=columns,
                drop=False,
            )
        )
        columns = {
            "F": (N_WITH_COL_PROP, 2),
            "M": (N_WITH_COL_PROP, 2),
            "All": (N_WITH_ROW_PROP, 2),
        }
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="FBG Fasted <8.0 hrs",
                condition=(self.main_df[self.colname] < 8.0),
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
        return row_defs


class FastingOgttTable(Table):
    def __init__(self, main_df: pd.DataFrame = None):
        super().__init__(colname="fasting_ogtt_hrs", main_df=main_df, title="")

    @property
    def row_definitions(self) -> RowDefinitions:
        row_defs = RowDefinitions(reverse_rows=False)
        columns = {
            "F": (MEDIAN_IQR, 2),
            "M": (MEDIAN_IQR, 2),
            "All": (MEDIAN_IQR, 2),
        }
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="OGTT fasted (hours), median (IQR)",
                condition=(self.main_df[self.colname].notna()),
                columns=columns,
                drop=False,
            )
        )
        columns = {
            "F": (N_WITH_COL_PROP, 2),
            "M": (N_WITH_COL_PROP, 2),
            "All": (N_WITH_ROW_PROP, 2),
        }
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="OGTT Fasted <8.0 hrs",
                condition=(self.main_df[self.colname] < 8.0),
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
        return row_defs


class FastingTable(Table):
    def __init__(self, main_df: pd.DataFrame = None):
        super().__init__(main_df=main_df, title="Fasting duration (hrs)")

    def build_table_df(self) -> None:
        df1 = FastingFbgTable(main_df=self.main_df).table_df
        df2 = FastingOgttTable(main_df=self.main_df).table_df
        self.table_df = pd.concat([df1, df2])
