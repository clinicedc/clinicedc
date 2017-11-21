from ..df_handlers import NonCrfDfHandler
from .csv_tables_exporter import CsvTablesExporter


class CsvExporterNoTables(Exception):
    pass


class CsvNonCrfTablesExporterError(Exception):
    pass


class CsvNonCrfTablesExporter(CsvTablesExporter):

    """A class to export non-CRF tables for this app_label.
    """

    without_visit_columns = None  # a list of columns to NOT appear in any table
    crf_dialect_cls = NonCrfDfHandler

    def __init__(self, without_columns=None, without_visit_columns=None, **kwargs):
        without_visit_columns = without_visit_columns or self.without_visit_columns or []
        without_columns = without_columns or []
        without_columns.extend(without_visit_columns)
        super().__init__(without_columns=without_columns, **kwargs)
