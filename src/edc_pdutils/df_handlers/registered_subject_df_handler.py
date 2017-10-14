import pandas as pd

from ..dialects import RsDialect
from ..constants import SYSTEM_COLUMNS
from .df_handler import DfHandler


class RegisteredSubjectDfHandler(DfHandler):

    rs_dialect_cls = RsDialect

    registered_subject_tbl = 'edc_registration_registeredsubject'
    registered_subject_column = 'registered_subject_id'
    system_columns = SYSTEM_COLUMNS
    sort_by = ['subject_identifier']
    exclude_export_columns = True
    exclude_system_columns = False

    def __init__(self, exclude_system_columns=None, **kwargs):
        self._df_registered_subject = pd.DataFrame()
        self.rs_dialect = self.rs_dialect_cls(self)
        self.exclude_system_columns = exclude_system_columns or self.exclude_system_columns
        super().__init__(**kwargs)

    def prepare_dataframe(self, **kwargs):
        """Merges CRF dataframe with df_visit_and_related
        on visit_column.
        """
        self.dataframe = pd.merge(
            left=self.dataframe, right=self.df_visit_and_related,
            how='left', on=self.visit_column,
            suffixes=['_notused', ''])
        self.dataframe = self.dataframe[self.columns]

    @property
    def columns(self):
        """Returns a list of column names.
        """
        df_columns = list(self.dataframe.columns)
        df_columns.pop(df_columns.index(self.registered_subject_column))
        columns = list(self.df_registered_subject.columns)
        columns.extend([c for c in df_columns if c not in columns])
        # "export_" columns
        if self.exclude_export_columns:
            columns = [col for col in columns if not col.startswith('export_')]
        # "system" columns, move to the end
        if not self.exclude_system_columns:
            columns = [col for col in columns if col not in self.system_columns]
            columns.extend(self.system_columns)
        return columns

    @property
    def df_registered_subject(self):
        """Returns a dataframe of the crf_dialect's `select_visit_and_related`
        SQL statement.
        """
        if self._df_registered_subject.empty:
            sql, params = self.rs_dialect_cls.select_registered_subject
            self._df_registered_subject = self.db.read_sql(sql, params=params)
        return self._df_registered_subject
