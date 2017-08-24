import numpy as np

from ..mysql import Dialect


class DfPrepperUnexpectedRowCount(Exception):
    pass


class DfPrepperDuplicateColumn(Exception):
    pass


class DfPrepper:

    na_value = np.nan
    sort_by = None
    dialect_cls = Dialect

    def __init__(self, dataframe=None, db=None, sort_by=None, na_value=None, **kwargs):

        original_row_count = len(dataframe.index)
        self.na_value = self.na_value if na_value is None else na_value
        self.sort_by = self.sort_by if sort_by is None else sort_by

        self.db = db
        self.dialect = self.dialect_cls(**kwargs)

        # raise on duplicate column
        cols = list(dataframe.columns)
        diff = set([x for x in cols if cols.count(x) > 1])
        if len(diff) > 0:
            raise DfPrepperDuplicateColumn(
                f'Duplicate column detected. Got {list(diff)}')

        dataframe = self.prepare_dataframe(dataframe)

        dataframe = self.finish_dataframe(dataframe)

        # verify size has not changed
        if original_row_count != len(dataframe.index):
            raise DfPrepperUnexpectedRowCount(
                f'Dataframe count has changed. Expected {original_row_count}. '
                f'Got {len(dataframe.index)} ')

        self.dataframe = dataframe

    def prepare_dataframe(self, dataframe=None, **kwargs):
        return dataframe

    def finish_dataframe(self, dataframe=None, **kwargs):
        for column in list(dataframe.select_dtypes(
                include=['datetime64[ns, UTC]']).columns):
            self.dataframe[column] = dataframe[
                column].astype('datetime64[ns]')
        dataframe.fillna(value=self.na_value, inplace=True)
        if self.sort_by:
            dataframe.sort_values(by=self.sort_by, inplace=True)
        return dataframe
