import pandas as pd

from edc_constants.constants import FEMALE, MALE

from ..constants import N_ONLY, N_WITH_COL_PROP, N_WITH_ROW_PROP
from ..row import RowDefinition, RowDefinitions
from ..table import Table


class ArtTable(Table):
    def __init__(self, main_df: pd.DataFrame = None):
        super().__init__(colname=None, main_df=main_df, title="HIV Care")

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

        cond_art_stable = (
            (df_tmp["on_rx_stable"] == "Yes")
            & (df_tmp["vl_undetectable"] == "Yes")
            & (df_tmp["art_six_months"] == "Yes")
        )
        row_defs.add(
            RowDefinition(
                label="Stable on ART (6m)",
                condition=cond_art_stable,
                columns=columns,
                drop=True,
            )
        )

        # look for anyone that is not stable by these three values
        condition_partially_stable = (
            (df_tmp["on_rx_stable"] == "Yes")
            | (df_tmp["vl_undetectable"] == "Yes")
            | (df_tmp["art_six_months"] == "Yes")
        )
        row_defs.add(
            RowDefinition(
                label="Other stable (`VL` or `on ART` or `stable 6m`)",
                condition=condition_partially_stable,
                columns=columns,
                drop=True,
            )
        )

        condition_other = (
            (df_tmp["on_rx_stable"] == "No")
            | (df_tmp["vl_undetectable"] == "No")
            | (df_tmp["art_six_months"] == "No")
        )

        row_defs.add(
            RowDefinition(
                label="Other",
                condition=condition_other,
                columns=columns,
                drop=True,
            )
        )

        condition_not_recorded = (
            (df_tmp["on_rx_stable"].isna())
            & (df_tmp["vl_undetectable"].isna())
            & (df_tmp["art_six_months"].isna())
        )
        row_defs.add(
            RowDefinition(
                label="Not recorded",
                condition=condition_not_recorded,
                columns=columns,
                drop=True,
            )
        )
        return row_defs
