import pandas as pd

from .crf_dialect import CrfDialect
from .df_prepper import DfPrepper


class CrfDfPrepper(DfPrepper):

    crf_dialect_cls = CrfDialect
    visit_column = 'subject_visit_id'
    visit_tbl = None

    appointment_tbl = 'edc_appointment_appointment'
    registered_subject_tbl = 'edc_registration_registeredsubject'
    system_columns = [
        'created', 'modified', 'user_created', 'user_modified',
        'hostname_created', 'hostname_modified', 'revision']
    visit_definition_tbl = 'edc_visit_schedule_visitdefinition'
    sort_by = ['subject_identifier', 'visit_datetime']

    def __init__(self, **kwargs):
        self._df_visit_and_related = pd.DataFrame()
        self.crf_dialect = self.crf_dialect_cls(self)
        super().__init__(**kwargs)

    def prepare_dataframe(self, **kwargs):
        crf_columns = list(self.dataframe.columns)
        crf_columns.pop(crf_columns.index(self.visit_column))
        columns = list(self.df_visit_and_related.columns)
        self.dataframe = pd.merge(
            left=self.dataframe, right=self.df_visit_and_related,
            how='left', on=self.visit_column,
            suffixes=['_xx', ''])
        columns.extend([c for c in crf_columns if c not in columns])
        # remove export columns
        columns = [col for col in columns if not col.startswith('export')]
        # move system columns to the end
        columns = [col for col in columns if col not in self.system_columns]
        columns.extend(self.system_columns)
        self.dataframe = self.dataframe[columns]

    @property
    def df_visit_and_related(self):
        """Returns a dataframe of the crf_dialect's `select_visit_and_related`
        SQL statement.
        """
        if self._df_visit_and_related.empty:
            self._df_visit_and_related = self.db.read_sql(
                self.crf_dialect.select_visit_and_related)
        return self._df_visit_and_related
