from .csv_tables_exporter import CsvTablesExporter


class CsvExporterNoTables(Exception):
    pass


class CsvCrfTablesExporter(CsvTablesExporter):

    visit_column = None

    def get_table_names(self, app_label=None, visit_column=None, **kwargs):
        if visit_column:
            self.visit_column = visit_column
        df = self.db.show_tables_with_columns(app_label, [self.visit_column])
        table_names = [
            tbl for tbl in list(df.table_name)
            if not any([tbl.startswith(app_label) for app_label in self.excluded_app_labels])]
        if not table_names:
            raise CsvExporterNoTables(
                f'No tables. Got app_label=\'{app_label}\', visit_column=\'{visit_column}\'.')
        return table_names
