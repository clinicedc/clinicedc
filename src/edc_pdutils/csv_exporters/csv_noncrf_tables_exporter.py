from ..df_handlers import NonCrfDfHandler
from .csv_crf_tables_exporter import CsvCrfTablesExporter


class CsvExporterNoTables(Exception):
    pass


class CsvNonCrfTablesExporterError(Exception):
    pass


class CsvNonCrfTablesExporter(CsvCrfTablesExporter):

    """A class to export non-CRF tables for this app_label.
    """

    visit_column = None  # column to NOT appear in any table
    crf_dialect_cls = NonCrfDfHandler

    def get_table_names(self):
        """Returns a list of table names of tables for this
        app_label that DO NOT have column `visit_column`.
        """
        df = self.db.show_tables_without_columns(
            app_label=self.app_label,
            column_names=[self.visit_column])
        return list(df.table_name)
