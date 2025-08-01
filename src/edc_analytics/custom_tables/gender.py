import pandas as pd

from ..table import Table


class GenderTable(Table):
    def __init__(self, main_df: pd.DataFrame = None):
        super().__init__(
            colname="gender",
            main_df=main_df,
            title="Gender",
        )
