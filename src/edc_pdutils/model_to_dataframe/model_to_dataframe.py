import numpy as np
import pandas as pd
import sys

from copy import copy
from django.apps import apps as django_apps
from django.db.models.constants import LOOKUP_SEP

from .value_getter import ValueGetter
from django.core.exceptions import FieldError


class ModelToDataframe:
    """
        m = ModelToDataframe(model='edc_pdutils.crf', add_columns_for=['clinic_visit'])
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
        self.m2m_columns = []
        self.add_columns_for = add_columns_for or []
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
                self.merge_dataframe_with_pivoted_m2ms()
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

    def merge_dataframe_with_pivoted_m2ms(self):
        """For each m2m field, merge in a single pivoted field.
        """
        for m2m in self.queryset.model._meta.many_to_many:
            try:
                m2m_qs = self.queryset.model.objects.filter(
                    **self.query_filter).values_list(
                    'id', f'{m2m.name}__short_name')
            except FieldError:
                pass
            else:
                df_m2m = pd.DataFrame.from_records(
                    list(m2m_qs), columns=['id', m2m.name])
                df_m2m = df_m2m[df_m2m[m2m.name].notnull()]
                df_pivot = pd.pivot_table(
                    df_m2m, values=m2m.name, index=['id'],
                    aggfunc=lambda x: ';'.join(str(v) for v in x))
                self._dataframe = pd.merge(
                    self._dataframe, df_pivot, how='left', on='id')

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
        for field in self.queryset.model._meta.fields:
            if hasattr(field, 'field_cryptor'):
                return True
        return False

    @property
    def encrypted_columns(self):
        """Return a list of column names that use encryption.
        """
        if not self._encrypted_columns:
            self._encrypted_columns = ['identity_or_pk']
            for field in self.queryset.model._meta.fields:
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
            columns_list = list(self.queryset[0].__dict__.keys())
            for name in self.sys_field_names:
                try:
                    columns_list.remove(name)
                except ValueError:
                    pass
            columns = dict(zip(columns_list, columns_list))
            for column_name in columns_list:
                if (column_name.endswith('_visit')
                        or column_name.endswith('_visit_id')):
                    columns = self.add_columns_for_subject_visit(
                        column_name=column_name,
                        columns=columns)
                if (column_name.endswith('_requisition')
                        or column_name.endswith('requisition_id')):
                    columns = self.add_columns_for_subject_requisitions(
                        columns=columns)

            self._columns = columns
        return self._columns

    def add_columns_for_subject_visit(self, column_name=None, columns=None):
        try:
            del columns['subject_identifier']
        except KeyError:
            columns.update({
                f'{column_name}__appointment__subject_identifier':
                'subject_identifier'})
        columns.update({
            f'{column_name}__appointment__appt_datetime':
            'appointment_datetime'})
        columns.update({
            f'{column_name}__appointment__visit_code':
            'visit_code'})
        columns.update({
            f'{column_name}__appointment__visit_code_sequence':
            'visit_code_sequence'})
        columns.update({
            f'{column_name}__report_datetime': 'visit_datetime'})
        columns.update({
            f'{column_name}__reason': 'visit_reason'})
        return columns

    def add_columns_for_subject_requisitions(self, columns=None):
        for col in copy(columns):
            if col.endswith('_requisition_id'):
                col_prefix = col.split('_')[0]
                column_name = col.split('_id')[0]
                columns.update({
                    f'{column_name}__requisition_identifier':
                    f'{col_prefix}_requisition_identifier'})
                columns.update({
                    f'{column_name}__drawn_datetime': f'{col_prefix}_drawn_datetime'})
                columns.update({
                    f'{column_name}__is_drawn': f'{col_prefix}_is_drawn'})
        return columns
