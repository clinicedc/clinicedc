
class ColumnApply:

    column_names = None

    def __init__(self, dataframe=None):
        self.dataframe = dataframe
        for column_name in self.column_names:
            if column_name in list(self.dataframe.columns):
                self._apply(column_name)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.column_names})'

    def _apply(self, column_name):
        self.dataframe[column_name] = self.dataframe[column_name].apply(
            self.apply)

    def apply(self, value):
        return value
