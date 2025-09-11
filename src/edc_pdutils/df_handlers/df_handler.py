import numpy as np


class DfHandlerUnexpectedRowCount(Exception):
    pass


class DfHandlerDuplicateColumn(Exception):
    pass


class DfHandler:
    column_handler_cls = None
    na_value = np.nan
    sort_by = None

    def __init__(
        self,
        dataframe=None,
        db=None,
        sort_by=None,
        na_value=None,
        table_name=None,
        **kwargs,
    ):
        self.table_name = table_name
        self.dataframe = dataframe
        original_row_count = len(self.dataframe.index)
        self.na_value = self.na_value if na_value is None else na_value
        self.sort_by = self.sort_by if sort_by is None else sort_by

        self.db = db

        # raise on duplicate column
        cols = list(self.dataframe.columns)
        diff = set([x for x in cols if cols.count(x) > 1])
        if len(diff) > 0:
            raise DfHandlerDuplicateColumn(f"Duplicate column detected. Got {list(diff)}")

        self.prepare_dataframe()
        self.finish_dataframe()

        # verify size has not changed
        if original_row_count != len(self.dataframe.index):
            raise DfHandlerUnexpectedRowCount(
                f"Dataframe count has changed. Expected {original_row_count}. "
                f"Got {len(self.dataframe.index)} "
            )

    def __repr__(self):
        return f"{self.__class__.__name__}(table_name={self.table_name})"

    def prepare_dataframe(self, **kwargs):
        pass

    def finish_dataframe(self, **kwargs):
        if self.column_handler_cls:
            handler = self.column_handler_cls(self.dataframe)
            self.dataframe = handler.dataframe

        for column in list(
            self.dataframe.select_dtypes(include=["datetime64[ns, UTC]"]).columns
        ):
            self.dataframe[column] = self.dataframe[column].astype("datetime64[ns]")
        self.dataframe.fillna(value=self.na_value, inplace=True)
        if self.sort_by:
            self.dataframe.sort_values(by=self.sort_by, inplace=True)
