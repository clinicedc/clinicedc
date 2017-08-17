import numpy as np
import pandas as pd
import sys

from django.apps import apps as django_apps
from django.db.models.constants import LOOKUP_SEP
from edc_export.model_exporter import ValueGetter
from pprint import pprint


class ModelToDataframe:
    """
        e = ModelToDataframe(model='edc_pdutils.crf', add_columns_for='clinic_visit')
        my_df = e.dataframe
    """

    value_getter_cls = ValueGetter

    def __init__(self, model=None, queryset=None, query_filter=None,
                 add_columns_for=None):
        query_filter = query_filter or {}
        if queryset:
            self.model = queryset.model._meta.label_lower
        else:
            self.model = model
        queryset = queryset or self.model_cls.objects.all()
        row_count = queryset.count()
        if row_count == 0:
            self.dataframe = pd.DataFrame()
        else:
            columns = self.columns(queryset, add_columns_for)
            if self.has_encrypted_fields:
                queryset = queryset.filter(**query_filter)
                data = []
                for index, model_obj in enumerate(queryset.order_by('id')):
                    sys.stdout.write(
                        f'{self.model} {index + 1}/{row_count} ... \r')
                    row = []
                    for lookup, column_name in columns.items():
                        lookups = None
                        if LOOKUP_SEP in lookup:
                            lookups = {column_name: lookup}
                        value_getter = self.value_getter_cls(
                            field_name=column_name,
                            model_obj=model_obj,
                            lookups=lookups)
                        row.append(value_getter.value)
                    data.append(row)
                    self.dataframe = pd.DataFrame(data, columns=columns)
                    sys.stdout.write(
                        f'{self.model} {row_count} / {row_count}  Done.\n')
            else:
                queryset = queryset.values_list(
                    *columns.keys()).filter(**query_filter)
                self.dataframe = pd.DataFrame(
                    list(queryset), columns=columns.keys())
            self.dataframe.rename(columns=columns, inplace=True)
            self.dataframe.fillna(value=np.nan, inplace=True)
            for column in list(self.dataframe.select_dtypes(
                    include=['datetime64[ns, UTC]']).columns):
                self.dataframe[column] = self.dataframe[
                    column].astype('datetime64[ns]')

    @property
    def model_cls(self):
        return django_apps.get_model(self.model)

    @property
    def has_encrypted_fields(self):
        """Returns True if at least one field uses encryption.
        """
        for field in self.model_cls._meta.fields:
            if hasattr(field, 'field_cryptor'):
                return True
        return False

    def columns(self, qs, add_columns_for):
        """Return a dictionary of column names.
        """
        columns = list(qs[0].__dict__.keys())
        columns = self.remove_sys_columns(columns)
        columns = dict(zip(columns, columns))
        if add_columns_for in columns or '{}_id'.format(add_columns_for) in columns:
            if add_columns_for.endswith('_visit'):
                columns.update({
                    '{}__appointment__visit_code'.format(add_columns_for):
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
