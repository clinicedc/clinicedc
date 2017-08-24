from .csv_tables_exporter import CsvTablesExporter


class CsvExporterNoTables(Exception):
    pass


class CsvCrfTablesExporterColumnError(Exception):
    pass


class CsvCrfTablesExporter(CsvTablesExporter):

    visit_column = None  # column to appear in all tables selected

    def get_table_names(self, app_label=None, visit_column=None, **kwargs):
        """Returns a list of table names of tables for this
        app_label that have column `visit_column`.
        """
        if visit_column:
            self.visit_column = visit_column
        if not self.visit_column:
            raise CsvCrfTablesExporter('Visit column not specified. Got None.')
        df = self.db.show_tables_with_columns(
            app_label, [self.visit_column])

        table_names = [
            tbl for tbl in list(df.table_name)
            if not any([tbl.startswith(app_label) for app_label in self.excluded_app_labels])]
        if not table_names:
            raise CsvExporterNoTables(
                f'No tables. Got app_label=\'{app_label}\', visit_column=\'{visit_column}\'.')
        return table_names
