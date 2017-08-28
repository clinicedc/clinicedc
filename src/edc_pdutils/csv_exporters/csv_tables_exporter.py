from ..database import Database
from ..df_preppers import DfPrepper
from .csv_exporter import CsvExporter


class CsvTablesExporterError(Exception):
    pass


class CsvTablesExporter:

    """Export to CSV all tables for an app_label.

    Usage:
        credentials = Credentials(
            user='user', passwd='passwd', dbname='bhp085',
            port='5001', host='td.bhp.org.bw')
        tables_exporter = CsvTablesExporter(app_label='td', credentials=credentials)
        tables_exporter = CsvTablesExporter(app_label='edc', credentials=credentials)

    """

    db_cls = Database
    excluded_app_labels = ['edc_sync']
    delimiter = '|'
    exclude_history_tables = False
    df_prepper_cls = DfPrepper
    csv_exporter_cls = CsvExporter

    def __init__(self, app_label=None, table_names=None,
                 **kwargs):
        self._table_names = None
        self.app_label = app_label
        self.db = self.db_cls(**kwargs)
        if table_names:
            for table_name in table_names:
                if table_name not in self.table_names:
                    raise CsvTablesExporterError(
                        f'Invalid table name for app_label={self.app_label}. '
                        f'Got {table_name}.')
            self._table_names = table_names
        if self.exclude_history_tables:
            self._table_names = [
                tbl for tbl in self.table_names
                if 'historical' not in tbl and not tbl.endswith('_audit')]
        self.export_tables_to_csv(**kwargs)

    def __repr__(self):
        return f'{self.__class__.__name__}(app_label=\'{self.app_label}\')'

    def export_tables_to_csv(self, **kwargs):
        """Exports all tables to CSV.
        """
        self.exported_paths = {}
        for table_name in self.table_names:
            df = self.to_df(table_name=table_name, **kwargs)
            csv_exporter = self.csv_exporter_cls(data_label=table_name)
            path = csv_exporter.to_csv(dataframe=df)
            if path:
                self.exported_paths.update({table_name: path})

    @property
    def table_names(self):
        """Returns a list of table names for this app_label.
        """
        if not self._table_names:
            df = self.db.show_tables(self.app_label)
            self._table_names = list(df.table_name)
        return self._table_names

    def to_df(self, table_name=None, **kwargs):
        """Returns a "prepped" dataframe for this table_name.
        """
        df = self.get_raw_df(table_name)
        return self.get_prepped_df(table_name, df, **kwargs)

    def get_raw_df(self, table_name=None):
        """Returns a df for the given table_name
        from an SQL statement, that is; raw).
        """
        return self.db.select_table(table_name=table_name)

    def get_prepped_df(self, table_name=None, df=None, **kwargs):
        """Returns a dataframe after passing the given df
        through the df_prepper class.
        """
        if self.df_prepper_cls:
            df_prepper = self.df_prepper_cls(
                dataframe=df, db=self.db,
                table_name=table_name, **kwargs)
            df = df_prepper.dataframe
        return df
