import pandas as pd
import numpy as np


class ModelToDataFrame(object):
    """
        e = EdcModelToDataFrame(ClinicVlResult, add_columns_for='clinic_visit')
        my_df = e.dataframe
    """

    def __init__(self, model=None, queryset=None, query_filter=None,
                 add_columns_for=None):
        query_filter = query_filter or {}
        qs = queryset or model.objects.all()
        self.model = model or qs.model
        columns = self.columns(qs, add_columns_for)
        if self.has_encrypted_fields:
            qs = qs.filter(**query_filter)
            self.dataframe = pd.DataFrame(
                [[getattr(obj, key) for key in columns]
                 for obj in qs], columns=columns)
        else:
            qs = qs.values_list(*columns.keys()).filter(**query_filter)
            self.dataframe = pd.DataFrame(list(qs), columns=columns.keys())
        self.dataframe.rename(columns=columns, inplace=True)
        self.dataframe.fillna(value=np.nan, inplace=True)
        for column in list(self.dataframe.select_dtypes(
                include=['datetime64[ns, UTC]']).columns):
            self.dataframe[column] = self.dataframe[
                column].astype('datetime64[ns]')

    @property
    def has_encrypted_fields(self):
        """Returns True if at least one field uses encryption.
        """
        for field in self.model._meta.fields:
            if hasattr(field, 'field_cryptor'):
                return True
        return False

    def columns(self, qs, add_columns_for):
        """Return a dictionary of column names.
        """
        columns = qs[0].__dict__.keys()
        columns = self.remove_sys_columns(columns)
        columns = dict(zip(columns, columns))
        if add_columns_for in columns or '{}_id'.format(add_columns_for) in columns:
            if add_columns_for.endswith('_visit'):
                columns.update({
                    '{}__appointment__code'.format(add_columns_for):
                    'visit_code'})
                try:
                    del columns['subject_identifier']
                except KeyError:
                    columns.update({
                        '{}__appointment__subject_identifier'.format(add_columns_for):
                        'subject_identifier'})
        return columns

    def remove_sys_columns(self, columns):
        names = ['_state', '_user_container_instance', 'using']
        for name in names:
            try:
                columns.remove(name)
            except ValueError:
                pass
        return columns
