from ..df_handlers import CrfDfHandler
from .csv_tables_exporter import CsvTablesExporter


class CsvExporterNoTables(Exception):
    pass


class CsvCrfTablesExporterError(Exception):
    pass


class CsvCrfTablesExporter(CsvTablesExporter):

    """A class to export CRF tables for this app_label.

    CRF tables include a FK to the visit model.
    """

    visit_column = None  # the visit column name used to select "CRF" tables
    df_handler_cls = CrfDfHandler

    def __init__(self, visit_column=None, with_columns=None, **kwargs):
        if visit_column:
            self.visit_column = visit_column
        if not self.visit_column:
            raise CsvCrfTablesExporterError(
                'Visit column not specified. Got None.')
        with_columns = with_columns or []
        with_columns.extend([self.visit_column])
        super().__init__(with_columns=with_columns, **kwargs)

    def __repr__(self):
        return (f'{self.__class__.__name__}(app_label=\'{self.app_label}\','
                f'visit_column=\'{self.visit_column}\')')
