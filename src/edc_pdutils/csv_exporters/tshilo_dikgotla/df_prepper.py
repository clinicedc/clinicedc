import pandas as pd

from ...df_prepper import DfPrepper as DefaultPrepper
from pprint import pprint


class Dialect:

    def select_visit(self, visit_tbl=None, visit_column=None):
        return (
            'SELECT R.subject_identifier, R.screening_identifier, R.dob, R.gender, R.subject_type, R.sid, '
            'V.report_datetime as visit_datetime, A.appt_status, '
            'VDEF.code as visit_code, VDEF.title as visit_title, VDEF.time_point, V.reason, '
            'A.appt_datetime, A.timepoint_datetime, A.best_appt_datetime, '
            'R.screening_age_in_years, R.registration_status, R.registration_datetime, '
            f'R.randomization_datetime, V.survival_status, V.last_alive_date, '
            f'V.id as {visit_column} '
            'from edc_appointment_appointment as A '
            f'LEFT JOIN {visit_tbl} as V on A.id=V.appointment_id '
            'LEFT JOIN edc_visit_schedule_visitdefinition as VDEF on A.visit_definition_id=VDEF.id '
            'LEFT JOIN edc_registration_registeredsubject as R on A.registered_subject_id=R.id')


class DfPrepper:

    default_prepper_cls = DefaultPrepper
    visit_column = 'maternal_visit_id'
    visit_tbl = 'td_maternal_maternalvisit'
    appointment_tbl = 'edc_appointment_appointment'
    registered_subject_tbl = 'edc_registration_registeredsubject'
    visit_definition_tbl = 'edc_visit_schedule_visitdefinition'
    dialect_cls = Dialect
    system_columns = ['created', 'modified', 'user_created', 'user_modified',
                      'hostname_created', 'hostname_modified', 'revision']

    def __init__(self, dataframe=None, db=None):
        self.db = db
        self.dialect = self.dialect_cls()
        df_visit = self.db.read_sql(
            self.dialect.select_visit(self.visit_tbl, self.visit_column))
        crf_columns = list(dataframe.columns)
        crf_columns.pop(crf_columns.index(self.visit_column))
        columns = list(df_visit.columns)
        dataframe = pd.merge(
            left=dataframe, right=df_visit,
            how='left', on=self.visit_column,
            suffixes=['', '_xx'])
        columns.extend(crf_columns)
        # remove export columns
        columns = [col for col in columns if not col.startswith('export')]
        # move system columns to the end
        columns = [col for col in columns if col not in self.system_columns]
        columns.extend(self.system_columns)
        dataframe = dataframe[columns]
        self.dataframe = self.default_prepper_cls(
            dataframe=dataframe).dataframe
