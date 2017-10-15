import pandas as pd

from .table import Table


class Visit(Table):

    default_columns = ['id', 'subject_identifier',
                       'report_datetime', 'visit_code']

    def prepare(self, df_subjects=None, **kwargs):
        self.dataframe = self.dataframe.rename(
            columns={'id': 'subject_visit_id', 'report_datetime': 'visit_datetime'})
        self.columns[self.columns.index('report_datetime')] = [
            'visit_datetime']
        self.columns[self.columns.index('id')] = [
            'subject_visit_id']
        self.dataframe['visit_datetime'] = self.helper.to_local_datetime(
            self.dataframe['visit_datetime'])
        self.dataframe['visit_date'] = self.dataframe['visit_datetime'].dt.normalize()
        self.columns.append('visit_date')
        self.dataframe = pd.merge(self.dataframe, df_subjects,
                                  on='subject_identifier', how='left')

    def read_csv(self, **kwargs):
        super().read_csv(**kwargs)
        self.dataframe['visit_datetime'] = self.dataframe['visit_datetime'].astype(
            'datetime64[ns]')
        self.dataframe['visit_date'] = self.dataframe['visit_date'].astype(
            'datetime64[ns]')
        self.dataframe['consent_datetime'] = self.dataframe['consent_datetime'].astype(
            'datetime64[ns]')
        self.dataframe['consent_date'] = self.dataframe['consent_date'].astype(
            'datetime64[ns]')
