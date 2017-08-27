from ..df_preppers import NonCrfDfPrepper
from .csv_crf_tables_exporter import CsvCrfTablesExporter


class CsvExporterNoTables(Exception):
    pass


class CsvNonCrfTablesExporterError(Exception):
    pass


class CsvNonCrfTablesExporter(CsvCrfTablesExporter):

    """A class to export non-CRF tables for this app_label.
    """

    visit_column = None  # column to NOT appear in any table
    crf_dialect_cls = NonCrfDfPrepper

    @property
    def table_names(self):
        """Returns a list of table names of tables for this
        app_label that DO NOT have column `visit_column`.
        """
        if not self._table_names:
            df = self.db.show_tables_without_columns(
                app_label=self.app_label,
                column_names=[self.visit_column])
            self._table_names = list(df.table_name)
        return self._table_names
