import sys
import pandas as pd

from .table import Table


class Consent(Table):

    default_columns = ['subject_identifier', 'gender',
                       'dob', 'consent_datetime', 'study_site']

    def prepare(self, **kwargs):
        self.dataframe['dob'] = self.helper.date_to_local_datetime(
            self.dataframe['dob'])
        self.dataframe['consent_datetime'] = self.helper.to_local_datetime(
            self.dataframe['consent_datetime'])
        self.dataframe = self.dataframe.sort_values(['subject_identifier'])
        self.dataframe = self.dataframe.drop_duplicates()
        self.dataframe = self.dataframe.groupby(
            ['subject_identifier', 'consent_datetime']).min().reset_index()
        self.dataframe['duplicate'] = self.dataframe.duplicated(self.dataframe)
        if len(self.dataframe[self.dataframe['duplicate']]) > 0:
            self.dataframe = self.deduplicate()
        self.dataframe['consent_date'] = self.dataframe['consent_datetime'].dt.normalize()
        self.columns.append('consent_date')

    def deduplicate(self):
        sys.stderr.write('Consent has duplicates!')
        sys.stderr.write(self.dataframe[self.dataframe['duplicate']])

    def read_csv(self, **kwargs):
        super().read_csv(**kwargs)
        self.dataframe['consent_datetime'] = self.dataframe['consent_datetime'].astype(
            'datetime64[ns]')
        self.dataframe['consent_date'] = self.dataframe['consent_date'].astype(
            'datetime64[ns]')
