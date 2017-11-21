import os
import pandas as pd

from datetime import datetime

from ..helper import Helper as BaseHelper
from .table_to_dataframe import TableToDataframe


class Helper(BaseHelper):

    to_dataframe_cls = TableToDataframe

    def get_raw_dataframe(self, table_name=None, drop_sys_columns=None,
                          csv_filename=None, path=None, timestamp=None):
        """Returns a dataframe.
        """
        if csv_filename:
            timestamp = timestamp or datetime.today().strftime('%Y%m%d%H%M%S')
            csv_filename = f'{table_name}_{timestamp}.csv'
            df_raw = self.to_dataframe_cls(
                table_name=table_name,
                drop_sys_columns=drop_sys_columns).dataframe
            df_raw.to_csv(os.path.join(path, csv_filename), index=False)
            print(os.path.join(path, csv_filename))
        else:
            df_raw = pd.read_csv(
                os.path.join(path, csv_filename), low_memory=False)
        return df_raw
