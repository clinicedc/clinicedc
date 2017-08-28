from ..df_preppers import CrfDfPrepper
from .csv_tables_exporter import CsvTablesExporter


class CsvExporterNoTables(Exception):
    pass


class CsvCrfTablesExporterError(Exception):
    pass


class CsvCrfTablesExporter(CsvTablesExporter):

    """A class to export CRF tables for this app_label.

    CRF tables include an FK to the visit model.
    """

    visit_column = None  # column to appear in all tables selected
    df_prepper_cls = CrfDfPrepper

    def __init__(self, visit_column=None, **kwargs):
        if visit_column:
            self.visit_column = visit_column
        if not self.visit_column:
            raise CsvCrfTablesExporterError(
                'Visit column not specified. Got None.')
        super().__init__(visit_column=self.visit_column, **kwargs)

    def __repr__(self):
        return (f'{self.__class__.__name__}(app_label=\'{self.app_label}\','
                f'visit_column=\'{self.visit_column}\')')

    @property
    def table_names(self):
        """Returns a list of table names for this
        app_label that have column `visit_column`.
        """
        if not self._table_names:
            df = self.db.show_tables_with_columns(
                self.app_label, [self.visit_column])
            self._table_names = list(df.table_name)
        return self._table_names
