from ..df_preppers import CrfDfPrepper
from .csv_tables_exporter import CsvTablesExporter


class CsvExporterNoTables(Exception):
    pass


class CsvCrfTablesExporterColumnError(Exception):
    pass


class CsvCrfTablesExporter(CsvTablesExporter):

    visit_column = None  # column to appear in all tables selected
    appointment_tbl = 'edc_appointment_appointment'
    registered_subject_tbl = 'edc_registration_registeredsubject'
    df_prepper_cls = CrfDfPrepper

    def __init__(self, visit_column=None, appointment_tbl=None,
                 registered_subject_tbl=None, **kwargs):
        if visit_column:
            self.visit_column = visit_column
        if not self.visit_column:
            raise CsvCrfTablesExporter('Visit column not specified. Got None.')
        self.appointment_tbl = appointment_tbl or self.appointment_tbl
        self.registered_subject_tbl = registered_subject_tbl or self.registered_subject_tbl
        super().__init__(visit_column=self.visit_column,
                         appointment_tbl=self.appointment_tbl,
                         registered_subject_tbl=self.registered_subject_tbl,
                         **kwargs)

    def get_table_names(self, app_label=None, **kwargs):
        """Returns a list of table names of tables for this
        app_label that have column `visit_column`.
        """
        df = self.db.show_tables_with_columns(
            app_label, [self.visit_column])

        table_names = [
            tbl for tbl in list(df.table_name)
            if not any([tbl.startswith(app_label) for app_label in self.excluded_app_labels])]
        if not table_names:
            raise CsvExporterNoTables(
                f'No tables. Got app_label=\'{app_label}\', visit_column=\'{self.visit_column}\'.')
        return table_names
