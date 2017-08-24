import numpy as np


class DfPrepperUnexpectedRowCount(Exception):
    pass


class DfPrepperDuplicateColumn(Exception):
    pass


class DfPrepper:

    na_value = np.nan
    sort_by = None
    date_format = 'YYYYMMDD'

    def __init__(self, dataframe=None, original_row_count=None,
                 sort_by=None, na_value=None, value_maps=None):
        self.na_value = self.na_value if na_value is None else na_value
        self.sort_by = self.sort_by if sort_by is None else sort_by
        self.dataframe = dataframe

        # raise on duplicate column
        cols = list(self.dataframe.columns)
        diff = set([x for x in cols if cols.count(x) > 1])
        if len(diff) > 0:
            raise DfPrepperDuplicateColumn(
                f'Duplicate column detected. Got {list(diff)}')

        for column in list(self.dataframe.select_dtypes(
                include=['datetime64[ns, UTC]']).columns):
            self.dataframe[column] = self.dataframe[
                column].astype('datetime64[ns]')

        if original_row_count != len(self.dataframe.index):
            raise DfPrepperUnexpectedRowCount(
                f'Dataframe count has changed. Expected {original_row_count}. '
                f'Got {len(self.dataframe.index)} ')

        self.dataframe.fillna(value=self.na_value, inplace=True)
        if self.sort_by:
            self.dataframe.sort_values(by=self.sort_by, inplace=True)
