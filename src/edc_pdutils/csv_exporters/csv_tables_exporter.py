from ..mysqldb import MysqlDb
from .csv_exporter import CsvExporter


class CsvTablesExporterError(Exception):
    pass


class CsvTablesExporter(CsvExporter):

    db_cls = MysqlDb

    def __init__(self, app_label=None, credentials=None, exclude_history=None, **kwargs):
        self.db = self.db_cls(credentials=credentials, **kwargs)
        df = self.db.show_tables(app_label)
        table_names = list(df.table_name)
        if exclude_history:
            table_names = [
                tbl for tbl in table_names
                if not tbl.endswith('history') and not tbl.endswith('_audit')]
        self.exported_paths = []
        for table_name in table_names:
            df = self.db.select_table(table_name)
            path = super().to_csv(label=table_name, dataframe=df)
            if path:
                self.exported_paths.append(path)
