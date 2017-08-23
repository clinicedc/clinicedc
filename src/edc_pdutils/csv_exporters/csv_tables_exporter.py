from ..df_prepper import DfPrepper
from ..mysqldb import MysqlDb
from .csv_exporter import CsvExporter


class CsvTablesExporterError(Exception):
    pass


class CsvTablesExporter(CsvExporter):

    db_cls = MysqlDb
    excluded_app_labels = ['edc_sync']
    df_prepper_cls = DfPrepper

    def __init__(self, app_label=None, table_names=None, credentials=None,
                 exclude_history=None, **kwargs):
        self.db = self.db_cls(credentials=credentials, **kwargs)
        if not table_names:
            table_names = self.get_table_names(app_label=app_label, **kwargs)
        if exclude_history:
            table_names = [
                tbl for tbl in table_names
                if not tbl.endswith('history') and not tbl.endswith('_audit')]
        self.exported_paths = []
        for table_name in table_names:
            df = self.db.select_table(table_name)
            if self.df_prepper_cls:
                df = self.df_prepper_cls(dataframe=df).dataframe
            path = super().to_csv(label=table_name, dataframe=df)
            if path:
                self.exported_paths.append(path)

    def get_table_names(self, app_label=None, **kwargs):
        df = self.db.show_tables(app_label)
        table_names = [
            tbl for tbl in list(df.table_name)
            if not any([tbl.startswith(app_label) for app_label in self.excluded_app_labels])]
        return table_names
