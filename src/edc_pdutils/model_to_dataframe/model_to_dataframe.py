import numpy as np
import pandas as pd
import sys

from django.apps import apps as django_apps
from django.db.models.constants import LOOKUP_SEP

from .value_getter import ValueGetter


class ModelToDataframe:
    """
        m = ModelToDataframe(model='edc_pdutils.crf', add_columns_for='clinic_visit')
        my_df = m.dataframe
    """

    value_getter_cls = ValueGetter
    sys_field_names = ['_state', '_user_container_instance', 'using']
    edc_sys_columns = [
        'created', 'modified',
        'user_created', 'user_modified',
        'hostname_created', 'hostname_modified',
        'device_created', 'device_modified',
        'revision']

    def __init__(self, model=None, queryset=None, query_filter=None,
                 add_columns_for=None, decrypt=None, drop_sys_columns=None,
                 **kwargs):
        self._columns = None
        self._encrypted_columns = None
        self._dataframe = pd.DataFrame()
        self.drop_sys_columns = drop_sys_columns
        self.decrypt = decrypt
        self.add_columns_for = add_columns_for
        self.query_filter = query_filter or {}
        if queryset:
            self.model = queryset.model._meta.label_lower
        else:
            self.model = model
        self.queryset = queryset or self.model_cls.objects.all()

    @property
    def dataframe(self):
        """Returns a pandas dataframe.
        """
        if self._dataframe.empty:
            row_count = self.queryset.count()
            if row_count > 0:
                if self.decrypt and self.has_encrypted_fields:
                    sys.stdout.write(
                        f'   PII will be decrypted! ... \n')
                    queryset = self.queryset.filter(**self.query_filter)
                    data = []
                    for index, model_obj in enumerate(queryset.order_by('id')):
                        sys.stdout.write(
                            f'   {self.model} {index + 1}/{row_count} ... \r')
                        row = []
                        for lookup, column_name in self.columns.items():
                            value = self.get_column_value(
                                model_obj=model_obj,
                                column_name=column_name,
                                lookup=lookup)
                            row.append(value)
                        data.append(row)
                        self._dataframe = pd.DataFrame(
                            data, columns=self.columns)
                else:
                    columns = [
                        col for col in self.columns if col not in self.encrypted_columns]
                    queryset = self.queryset.values_list(
                        *columns).filter(**self.query_filter)
                    self._dataframe = pd.DataFrame(
                        list(queryset), columns=columns)
                self._dataframe.rename(columns=self.columns, inplace=True)
                self._dataframe.fillna(value=np.nan, inplace=True)
                for column in list(self._dataframe.select_dtypes(
                        include=['datetime64[ns, UTC]']).columns):
                    self._dataframe[column] = self._dataframe[
                        column].astype('datetime64[ns]')
            if self.drop_sys_columns:
                self._dataframe = self._dataframe.drop(
                    self.edc_sys_columns, axis=1)
        return self._dataframe

    def get_column_value(self, model_obj=None, column_name=None, lookup=None):
        """Returns the column value.
        """
        lookups = {column_name: lookup} if LOOKUP_SEP in lookup else None
        value_getter = self.value_getter_cls(
            field_name=column_name,
            model_obj=model_obj,
            lookups=lookups)
        return value_getter.value

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

    @property
    def encrypted_columns(self):
        """Return a list of column names that use encryption.
        """
        if not self._encrypted_columns:
            self._encrypted_columns = ['identity_or_pk']
            for field in self.model_cls._meta.fields:
                if hasattr(field, 'field_cryptor'):
                    self._encrypted_columns.append(field.name)
            self._encrypted_columns = list(set(self._encrypted_columns))
            self._encrypted_columns.sort()
        return self._encrypted_columns

    @property
    def columns(self):
        """Return a dictionary of column names.
        """
        if not self._columns:
            columns = list(self.queryset[0].__dict__.keys())
            for name in self.sys_field_names:
                try:
                    columns.remove(name)
                except ValueError:
                    pass
            columns = dict(zip(columns, columns))
            columns = self.add_columns_for_subject_visit(columns)
            self._columns = columns
        return self._columns

    def add_columns_for_subject_visit(self, columns):
        if self.add_columns_for in columns or f'{self.add_columns_for}_id' in columns:
            if (self.add_columns_for.endswith('_visit')
                    or self.add_columns_for.endswith('_visit_id')):
                columns.update({
                    f'{self.add_columns_for}__appointment__appt_datetime':
                    'appointment_datetime'})
                columns.update({
                    f'{self.add_columns_for}__appointment__visit_code':
                    'visit_code'})
                columns.update({
                    f'{self.add_columns_for}__appointment__visit_code_sequence':
                    'visit_code_sequence'})
                columns.update({
                    f'{self.add_columns_for}__report_datetime': 'visit_datetime'})
                columns.update({
                    f'{self.add_columns_for}__reason': 'visit_reason'})
                try:
                    del columns['subject_identifier']
                except KeyError:
                    columns.update({
                        f'{self.add_columns_for}__appointment__subject_identifier':
                        'subject_identifier'})
        return columns
