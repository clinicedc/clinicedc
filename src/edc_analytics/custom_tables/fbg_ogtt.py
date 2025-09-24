import pandas as pd

from edc_constants.constants import FEMALE, MALE

from ..constants import N_ONLY, N_WITH_COL_PROP, N_WITH_ROW_PROP
from ..row import RowDefinition, RowDefinitions
from ..table import Table


class FbgOgttTable1(Table):

    fbg_colname = "fbg"
    ogtt_colname = "ogtt"

    def __init__(self, main_df: pd.DataFrame = None):
        super().__init__(
            colname="",
            main_df=main_df,
            title="OGTT & FBG (mmol/L) categories",
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
                colname=self.colname,
                label="Not fasted",
                condition=(
                    (self.main_df["fasting_fbg_hrs"] < 8.0)
                    | (self.main_df["fasting_ogtt_hrs"] < 8.0)
                ),
                columns=columns,
                drop=True,
            )
        )

        condition = (
            (self.main_df[self.ogtt_colname] >= 11.1)
            & (self.main_df[self.fbg_colname] >= 7.0)
            & (self.main_df[self.ogtt_colname].notna())
            & (self.main_df[self.fbg_colname].notna())
        )
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="OGTT ≥11.1 and FBG ≥7.0",
                condition=condition,
                columns=columns,
                drop=True,
            )
        )

        condition = (
            ((df_tmp[self.ogtt_colname] >= 11.1) | (df_tmp[self.fbg_colname] >= 7.0))
            & (df_tmp[self.fbg_colname].notna())
            & (df_tmp[self.ogtt_colname].notna())
        )

        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="OGTT ≥11.1 or FBG ≥7.0",
                condition=condition,
                columns=columns,
                drop=True,
            )
        )

        condition = (
            ((df_tmp[self.fbg_colname] >= 6.1) | (df_tmp[self.ogtt_colname] >= 7.8))
            & (df_tmp[self.fbg_colname].notna())
            & (df_tmp[self.ogtt_colname].notna())
        )
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="OGTT ≥7.8 or FBG ≥6.1",
                condition=condition,
                columns=columns,
                drop=True,
            )
        )

        condition = (
            ((df_tmp[self.fbg_colname] < 6.1) | (df_tmp[self.ogtt_colname] < 7.8))
            & (df_tmp[self.fbg_colname].notna())
            & (df_tmp[self.ogtt_colname].notna())
        )
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="OGTT <7.8 or FBG <6.1",
                condition=condition,
                columns=columns,
                drop=True,
            )
        )

        condition = (df_tmp[self.fbg_colname].notna()) & (df_tmp[self.ogtt_colname].notna())
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="Other",
                condition=condition,
                columns=columns,
                drop=True,
            )
        )

        condition = (df_tmp[self.fbg_colname].notna()) & (df_tmp[self.ogtt_colname].isna())
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="OGTT not measured",
                condition=condition,
                columns=columns,
                drop=True,
            )
        )
        condition = (df_tmp[self.fbg_colname].isna()) & (df_tmp[self.ogtt_colname].notna())
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="FBG not measured",
                condition=condition,
                columns=columns,
                drop=True,
            )
        )
        condition = (df_tmp[self.fbg_colname].isna()) & (df_tmp[self.ogtt_colname].isna())
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="not measured",
                condition=condition,
                columns=columns,
                drop=True,
            )
        )
        return row_defs


class FbgOgttTable2(Table):

    fbg_colname = "fbg"
    ogtt_colname = "ogtt"

    def __init__(self, main_df: pd.DataFrame = None):
        super().__init__(
            colname="",
            main_df=main_df,
            title="OGTT & FBG (mmol/L) additional",
        )

    @property
    def row_definitions(self) -> RowDefinitions:
        df_tmp = self.main_df.copy()
        row_defs = RowDefinitions(reverse_rows=False)
        row0 = RowDefinition(
            title=self.title,
            label="Glucose levels, n (%)",
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
                colname=self.colname,
                label="Not fasted",
                condition=(
                    (self.main_df["fasting_fbg_hrs"] < 8.0)
                    | (self.main_df["fasting_ogtt_hrs"] < 8.0)
                ),
                columns=columns,
                drop=True,
            )
        )

        condition = (
            (self.main_df[self.fbg_colname] < 6.1)
            & (self.main_df[self.ogtt_colname] < 7.8)
            & (self.main_df[self.ogtt_colname].notna())
            & (self.main_df[self.fbg_colname].notna())
        )
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="FBG <6.1 mmol/l and after OGTT <7.8 mmol/l",
                condition=condition,
                columns=columns,
                drop=True,
            )
        )

        condition = (
            (self.main_df[self.fbg_colname] < 6.1)
            & (self.main_df[self.ogtt_colname] >= 7.8)
            & (self.main_df[self.ogtt_colname] < 11.1)
            & (self.main_df[self.ogtt_colname].notna())
            & (self.main_df[self.fbg_colname].notna())
        )
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="FBG <6.1 mmol/l and after OGTT 7.8–11.0 mmol/l",
                condition=condition,
                columns=columns,
                drop=True,
            )
        )

        condition = (
            (self.main_df[self.fbg_colname] >= 6.1)
            & (self.main_df[self.fbg_colname] < 7.0)
            & (self.main_df[self.ogtt_colname] < 7.8)
            & (self.main_df[self.ogtt_colname].notna())
            & (self.main_df[self.fbg_colname].notna())
        )
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="FBG 6.1–6.9 mmol/l and after OGTT <7.8 mmol/l",
                condition=condition,
                columns=columns,
                drop=True,
            )
        )

        condition = (
            (self.main_df[self.fbg_colname] >= 6.1)
            & (self.main_df[self.fbg_colname] < 7.0)
            & (self.main_df[self.ogtt_colname] >= 7.8)
            & (self.main_df[self.ogtt_colname] < 11.1)
            & (self.main_df[self.ogtt_colname].notna())
            & (self.main_df[self.fbg_colname].notna())
        )
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="FBG 6.1–6.9 mmol/l and after OGTT 7.8–11.0 mmol/l",
                condition=condition,
                columns=columns,
                drop=True,
            )
        )

        condition = (
            (self.main_df[self.fbg_colname] >= 6.1)
            & (self.main_df[self.fbg_colname] < 7.0)
            & (self.main_df[self.ogtt_colname] >= 11.1)
            & (self.main_df[self.ogtt_colname].notna())
            & (self.main_df[self.fbg_colname].notna())
        )
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="FBG 6.1–6.9 mmol/l and after OGTT ≥11.0 mmol/l",
                condition=condition,
                columns=columns,
                drop=True,
            )
        )

        condition = (
            (self.main_df[self.fbg_colname] >= 7.0)
            & (self.main_df[self.ogtt_colname] < 7.8)
            & (self.main_df[self.ogtt_colname].notna())
            & (self.main_df[self.fbg_colname].notna())
        )
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="FBG ≥7.0 mmol/l and after OGTT <7.8 mmol/l",
                condition=condition,
                columns=columns,
                drop=True,
            )
        )

        condition = (
            (self.main_df[self.fbg_colname] >= 7.0)
            & (self.main_df[self.ogtt_colname] >= 7.8)
            & (self.main_df[self.ogtt_colname] < 11.1)
            & (self.main_df[self.ogtt_colname].notna())
            & (self.main_df[self.fbg_colname].notna())
        )
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="FBG ≥7.0 mmol/l and after OGTT 7.8–11.0 mmol/l",
                condition=condition,
                columns=columns,
                drop=True,
            )
        )

        condition = (
            (self.main_df[self.fbg_colname] >= 7.0)
            & (self.main_df[self.ogtt_colname] >= 11.1)
            & (self.main_df[self.ogtt_colname].notna())
            & (self.main_df[self.fbg_colname].notna())
        )
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="FBG ≥7.0 mmol/l and after OGTT ≥11.1 mmol/l",
                condition=condition,
                columns=columns,
                drop=True,
            )
        )

        condition = (self.main_df[self.ogtt_colname].notna()) | (
            self.main_df[self.fbg_colname].isna()
        )
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="FBG not measured",
                condition=condition,
                columns=columns,
                drop=True,
            )
        )

        condition = (self.main_df[self.ogtt_colname].isna()) | (
            self.main_df[self.fbg_colname].notna()
        )
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="OGTT not measured",
                condition=condition,
                columns=columns,
                drop=True,
            )
        )

        condition = (self.main_df[self.ogtt_colname].isna()) | (
            self.main_df[self.fbg_colname].isna()
        )
        row_defs.add(
            RowDefinition(
                colname=self.colname,
                label="not measured",
                condition=condition,
                columns=columns,
                drop=True,
            )
        )
        return row_defs


class FbgOgttTable(Table):

    def __init__(self, main_df: pd.DataFrame = None):
        super().__init__(colname="", main_df=main_df, title="")

    def build_table_df(self) -> None:
        df1 = FbgOgttTable1(main_df=self.main_df).table_df
        df2 = FbgOgttTable2(main_df=self.main_df).table_df
        self.table_df = pd.concat([df1, df2])
