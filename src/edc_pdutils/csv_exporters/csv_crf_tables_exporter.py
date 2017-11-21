from ..df_handlers import CrfDfHandler
from .csv_tables_exporter import CsvTablesExporter


class CsvExporterNoTables(Exception):
    pass


class CsvCrfTablesExporterError(Exception):
    pass


class CsvCrfTablesExporter(CsvTablesExporter):

    """A class to export CRF tables for this app_label.

    CRF tables include an FK to the visit model.
    """

    visit_columns = None  # a list of columns to appear in all tables selected
    df_handler_cls = CrfDfHandler

    def __init__(self, visit_columns=None, **kwargs):
        if visit_columns:
            self.visit_columns = visit_columns
        if not self.visit_columns:
            raise CsvCrfTablesExporterError(
                'Visit columns not specified. Got None.')
        super().__init__(with_columns=self.visit_columns, **kwargs)

    def __repr__(self):
        return (f'{self.__class__.__name__}(app_label=\'{self.app_label}\','
                f'visit_columns=\'{self.visit_columns}\')')
