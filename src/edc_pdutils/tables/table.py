import pandas as pd

from ..table_to_dataframe import TableToDataframe, Helper


class Table:

    default_columns = None
    helper_cls = Helper
    table_to_dataframe_cls = TableToDataframe

    def __init__(self, table_name=None, columns=None, filename=None, local_tz=None,
                 limit=None, **kwargs):
        self.dataframe = None
        self.helper = self.helper_cls(local_tz=local_tz)
        self.columns = columns or self.default_columns
        if filename:
            self.read_csv(filename=filename)
        else:
            self.dataframe = self.table_to_dataframe_cls(
                table_name=table_name,
                columns=self.columns,
                limit=limit).dataframe
            self.prepare(**kwargs)

    def prepare(self, **kwargs):
        pass

    def read_csv(self, filename=None):
        self.dataframe = pd.read_csv(filename, low_memory=False)
