import pandas as pd

from edc_pdutils.analysis import Table, default_columns


class GenderTable(Table):
    def __init__(self, main_df: pd.DataFrame = None):
        super().__init__(
            main_df=main_df, label="Gender", columns=default_columns, show_ncol_perc=True
        )
