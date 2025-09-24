import pandas as pd

from edc_constants.constants import FEMALE, MALE

from .constants import COUNT_COLUMN, N_ONLY, N_WITH_ROW_PROP, TITLE_COLUMN
from .row import RowDefinition, RowDefinitions, RowStatisticsWithGender


class Table:

    title_column = "Characteristics"
    label_column = "Statistic"
    default_sublabel = "n"
    gender_column = "gender"
    row_statistics_cls: RowStatisticsWithGender = RowStatisticsWithGender

    def __init__(
        self,
        colname: str | None = None,
        main_df: pd.DataFrame = None,
        title: str | None = None,
        include_zero_counts: bool | None = None,
    ):

        self.colname = colname
        self.main_df = main_df
        self.title = title
        self.include_zero_counts = include_zero_counts
        self.table_df: pd.DataFrame = pd.DataFrame()

        self.build_table_df()
        if self.title:
            # add a redundant column to hold title name for each
            # row in this table.
            self.table_df[TITLE_COLUMN] = self.title

    @property
    def row_definitions(self) -> RowDefinitions:
        """Override with your RowDefs

        The default adds a first row with gender breakdown.
        """
        row_defs = RowDefinitions(
            colname=self.colname, row_statistics_cls=self.row_statistics_cls
        )
        row_defs.add(
            RowDefinition(
                title=self.title,
                label=self.default_sublabel,
                colname=None,
                condition=(self.main_df[self.gender_column].notna()),
                columns={
                    FEMALE: (N_WITH_ROW_PROP, 2),
                    MALE: (N_WITH_ROW_PROP, 2),
                    "All": (N_ONLY, 2),
                },
                drop=False,
            )
        )
        return row_defs

    def reorder_df(self):
        """Override to reorder the rows in `table_df`."""
        pass

    def build_table_df(self) -> None:
        """Build the table_df using the row definitions."""
        df_denominator = self.main_df.copy()
        rows = []
        for index, rd in enumerate(self.row_definitions.definitions):
            if not rd.condition.empty:
                df_numerator = df_denominator.loc[rd.condition]
            else:
                # default to first col non-null values
                df_numerator = df_denominator.loc[
                    df_denominator[df_denominator.columns[0]].notna()
                ]
            row_stats = self.row_statistics_cls(
                colname=rd.colname,
                df_numerator=df_numerator,
                df_denominator=df_denominator,
                df_all=self.main_df,
                columns=rd.columns,
            )
            if index == 0:
                columns = (
                    [self.title_column, self.label_column]
                    + row_stats.labels()
                    + [TITLE_COLUMN]
                )
                # reset table_df
                self.table_df = pd.DataFrame(columns=columns)
            rows.append([rd.title, rd.label] + row_stats.values_list() + [self.title])
            if rd.drop and not df_numerator.empty:
                df_denominator.drop(df_numerator.index, inplace=True)
        if self.row_definitions.reverse_rows:
            rows.reverse()
        for index, values_list in enumerate(rows):
            self.table_df.loc[index] = values_list
        if not self.include_zero_counts:
            self.table_df.drop(
                self.table_df[self.table_df[COUNT_COLUMN] == 0].index, inplace=True
            )
        self.reorder_df()

    @property
    def formatted_df(self) -> pd.DataFrame:
        """Return DF with first 5 columns"""
        return self.table_df.iloc[:, :5]
