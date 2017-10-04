class ColumnMapError(Exception):
    pass


class ColumnMap:

    column_names = None
    mappings = {}

    def __init__(self, dataframe=None):
        self.dataframe = dataframe
        for column_name in self.column_names:
            if column_name in list(self.dataframe.columns):
                self._map(column_name)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.column_names})'

    def _map(self, column_name):
        mapping = self.mappings.get(column_name)
        if not mapping:
            raise ColumnMapError(f'Mapping not found for column {column_name}')
        self.dataframe[column_name] = self.dataframe[column_name].map(
            mapping.get)
