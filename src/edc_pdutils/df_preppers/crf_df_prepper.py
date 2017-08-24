import pandas as pd

from .df_prepper import DfPrepper
from pprint import pprint


class Dialect:

    def select_visit_and_related(self, visit_tbl=None, visit_column=None, **kwargs):
        """Returns an SQL statement that joins visit, appt, and registered_subject.

        This is for older EDC versions that use this schema.
        """
        return (
            'SELECT R.subject_identifier, R.screening_identifier, R.dob, R.gender, R.subject_type, R.sid, '
            'V.report_datetime as visit_datetime, A.appt_status, V.study_status, '
            'VDEF.code as visit_code, VDEF.title as visit_title, VDEF.time_point, V.reason, '
            'A.appt_datetime, A.timepoint_datetime, A.best_appt_datetime, '
            'R.screening_age_in_years, R.registration_status, R.registration_datetime, '
            'R.randomization_datetime, V.survival_status, V.last_alive_date, '
            f'V.id as {visit_column} '
            'from edc_appointment_appointment as A '
            f'LEFT JOIN {visit_tbl} as V on A.id=V.appointment_id '
            'LEFT JOIN edc_visit_schedule_visitdefinition as VDEF on A.visit_definition_id=VDEF.id '
            'LEFT JOIN edc_registration_registeredsubject as R on A.registered_subject_id=R.id '
        )


class CrfDfPrepper:

    dialect_cls = Dialect
    visit_column = 'subject_visit_id'
    visit_tbl = None

    appointment_tbl = 'edc_appointment_appointment'
    registered_subject_tbl = 'edc_registration_registeredsubject'
    system_columns = [
        'created', 'modified', 'user_created', 'user_modified',
        'hostname_created', 'hostname_modified', 'revision']
    visit_definition_tbl = 'edc_visit_schedule_visitdefinition'
    sort_by = ['subject_identifier', 'visit_datetime']
    default_prepper_cls = DfPrepper

    def __init__(self, dataframe=None, db=None):
        self._df_visit_and_related = pd.DataFrame()

        original_row_count = len(dataframe.index)
        self.db = db
        self.dialect = self.dialect_cls()

        crf_columns = list(dataframe.columns)
        crf_columns.pop(crf_columns.index(self.visit_column))
        columns = list(self.df_visit_and_related.columns)
        dataframe = pd.merge(
            left=dataframe, right=self.df_visit_and_related,
            how='left', on=self.visit_column,
            suffixes=['_xx', ''])
        columns.extend([c for c in crf_columns if c not in columns])
        # remove export columns
        columns = [col for col in columns if not col.startswith('export')]
        # move system columns to the end
        columns = [col for col in columns if col not in self.system_columns]
        columns.extend(self.system_columns)
        dataframe = dataframe[columns]

        prepper = self.default_prepper_cls(
            dataframe=dataframe,
            original_row_count=original_row_count,
            sort_by=self.sort_by)
        self.dataframe = prepper.dataframe

    @property
    def select_visit_and_related(self):
        """Returns an SQL statement of the visit table and any additional
        related fields, .e.g. fields from appointment and registered subject.
        """
        return self.dialect.select_visit_and_related(
            self.visit_tbl, self.visit_column)

    @property
    def df_visit_and_related(self):
        """Returns a dataframe of the `sql_select_visit_and_related`
        query.
        """
        if self._df_visit_and_related.empty:
            self._df_visit_and_related = self.db.read_sql(
                self.select_visit_and_related)
        return self._df_visit_and_related
