import numpy as np
import pandas as pd

from edc_constants.constants import YES

from ..mappings import yes_no
from .table import Table


class Crf(Table):

    default_columns = ['subject_visit_id', 'report_datetime',
                       'is_drawn', 'reason_not_drawn', 'drawn_datetime',
                       'specimen_type', 'study_site_name']

    def prepare(self, df_visit=None, **kwargs):
        self.dataframe['requisition_datetime'] = self.helper.to_local_datetime(
            self.dataframe['requisition_datetime'])
        self.dataframe['drawn_datetime'] = self.helper.to_local_datetime(
            self.dataframe['drawn_datetime'])
        self.dataframe['received_datetime'] = self.helper.to_local_datetime(
            self.dataframe['received_datetime'])
        self.dataframe['received'] = self.dataframe['received'].map(
            yes_no, na_action='ignore')
        self.dataframe['processed'] = self.dataframe['processed'].map(
            yes_no, na_action='ignore')
        self.dataframe['packed'] = self.dataframe['packed'].map(
            yes_no, na_action='ignore')
        self.dataframe['shipped'] = self.dataframe['shipped'].map(
            yes_no, na_action='ignore')
        self.dataframe = pd.merge(
            self.dataframe, df_visit, on='subject_visit_id', how='left')
        self.dataframe = self.dataframe.drop(['subject_visit_id'], axis=1)
        # fix reason_not_drawn
        is_blank = (self.dataframe.reason_not_drawn.notnull()) & (
            self.dataframe.is_drawn == YES)
        self.dataframe.loc[is_blank, 'reason_not_drawn'] = np.nan
        self.dataframe = self.dataframe[self.reordered_columns]

    @property
    def reordered_columns(self):
        columns = [col for col in list(self.dataframe.columns) if col not in [
            'subject_identifier', 'gender', 'dob',
            'visit_code', 'visit_datetime', 'visit_date']]
        columns.insert(0, 'visit_code')
        columns.insert(0, 'visit_date')
        columns.insert(0, 'visit_datetime')
        columns.insert(0, 'dob')
        columns.insert(0, 'gender')
        columns.insert(0, 'subject_identifier')
        return columns
