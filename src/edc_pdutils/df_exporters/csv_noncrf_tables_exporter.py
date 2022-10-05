from ..df_handlers import NonCrfDfHandler
from .tables_exporter import TablesExporter


class CsvExporterNoTables(Exception):
    pass


class CsvNonCrfTablesExporterError(Exception):
    pass


class CsvNonCrfTablesExporter(TablesExporter):

    """A class to export non-CRF tables for this app_label."""

    # a list of columns to NOT appear in any table, used to select the tables
    without_crf_columns = None
    crf_dialect_cls = NonCrfDfHandler

    def __init__(self, without_columns=None, without_crf_columns=None, **kwargs):
        without_crf_columns = without_crf_columns or self.without_crf_columns or []
        without_columns = without_columns or []
        without_columns.extend(without_crf_columns)
        super().__init__(without_columns=without_columns, **kwargs)
