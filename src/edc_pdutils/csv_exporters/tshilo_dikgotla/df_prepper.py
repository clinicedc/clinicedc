import pandas as pd

from ...df_prepper import DfPrepper as DefaultPrepper


class DfPrepper:

    default_prepper_cls = DefaultPrepper
    visit_column = 'maternal_visit_id'
    visit_tbl = 'td_maternal_maternalvisit'
    appointment_tbl = 'td_maternal_appointment'
    registered_subject_tbl = 'edc_registration_registeredsubject'

    def __init__(self, dataframe=None, db=None):
        self.db = db
        df_appt = self.db.select_table(self.appointment_tbl)
        df_rs = self.db.select_table(self.appointment_tbl)
        df = pd.merge(
            left=df_appt, right=df_rs,
            how='left', left_on='registered_subject_id', right_on='id',
            suffixes=['', '_rs'])
        cols = ['id', 'subject_identifier', 'gender', 'dob',
                'appt_datetime', 'code', 'appt_status', 'sid']
        df = df[cols]
        df_visit = self.db.select_table(self.visit_tbl)
        df = pd.merge(
            left=df_appt, right=df_visit,
            how='left', left_on='id', right_on='appointment_id',
            suffixes=['', '_visit'])
        cols = cols.extend('report_datetime', 'reason')
        df = df[cols]
        dataframe = pd.merge(
            left=dataframe, right=df,
            how='left', left_on=self.visit_column, right_on='id_visit',
            suffixes=['', '_xx'])
        dataframe = self.default_prepper_cls(dataframe=dataframe).dataframe
