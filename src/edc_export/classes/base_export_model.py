import csv
import json
import os
import string

from collections import OrderedDict
from datetime import datetime

from django.db.models.constants import LOOKUP_SEP

from django_crypto_fields.fields import BaseField as BaseEncryptedField

from ..models import ExportHistory
from django.utils import timezone

HEAD_FIELDS = [
    'export_uuid', 'export_datetime', 'export_change_type',
    'subject_identifier', 'report_datetime']
TAIL_FIELDS = [
    'hostname_created', 'hostname_modified', 'created',
    'modified', 'user_created', 'user_modified', 'revision']


class BaseExportModel(object):
    def __init__(self, queryset, model=None, modeladmin=None, fields=None, exclude=None, extra_fields=None,
                 header=True, track_history=False, show_all_fields=True, delimiter=None, encrypt=True,
                 strip=False, notification_plan_name=None, export_datetime=None):
        self._file_obj = None
        self._header_from_m2m_complete = False
        self._model = None
        self._m2m_value_delimiter = ';'

        self.encrypt = encrypt
        self.delimiter = ',' if delimiter is None else delimiter
        self.header_row = []
        self.include_header_row = header
        try:
            self.model = modeladmin.model
        except AttributeError:
            self.model = model
        self.queryset = queryset
        self.row = None
        self.row_instance = None
        self.show_all_fields = show_all_fields
        self.strip = strip
        self.track_history = True if track_history is None else track_history
        self.notification_plan_name = notification_plan_name

        self.extra_fields = extra_fields or OrderedDict({})
        self.field_names = [field.name for field in self.model._meta.fields] if self.show_all_fields else []
        # a list of names from admin usually, may create duplicates that will be removed
        self.field_names.extend(fields or [])
        for field_name in self.field_names:
            # remove items if already listed in field_names
            self.extra_fields.pop(field_name, None)
        self.field_names.extend(self.extra_fields.keys() or [])
        self.field_names = list(OrderedDict.fromkeys(self.field_names))  # remove duplicates, maintain order
        self.insert_defaults_and_reorder_field_names()
        self.exclude_field_names(exclude)  # a list of names
        self.header_row = self.field_names
        try:
            export_datetime = export_datetime.strftime('%Y%m%d%H%M%S')
        except AttributeError:
            export_datetime = timezone.now().strftime('%Y%m%d%H%M%S')
        self.export_filename = '{0}_{1}.csv'.format(
            unicode(self.model._meta).replace('.', '_'),
            export_datetime)
        self.export_history = None

    def write_to_file(self):
        """Writes the export file and returns the file name."""
        exported_pk_list = []
        export_uuid_list = []
        export_file_contents = []
        with open(os.path.join(os.path.expanduser(self.target_path) or '', self.export_filename), 'w') as f:
            writer = csv.writer(f, delimiter=self.delimiter)
            if self.include_header_row:
                self.header_row.insert(1, 'timestamp')
                writer.writerow(self.header_row)
                export_file_contents.append(self.header_row)
            seen = set()
            for self.row_instance in self.queryset:
                self.row = self.fetch_row()
                if self.remove_duplicates:
                    if json.dumps(self.row) in seen:
                        self.update_export_transaction(self.row_instance)
                        continue  # skip duplicates
                    seen.add(json.dumps(self.row))
                self.row[1] = self.row_instance.export_transaction.timestamp
                writer.writerow(self.row)
                export_file_contents.append(self.row)
                self.update_export_transaction(self.row_instance)
                exported_pk_list.append(self.row_instance.pk)
                export_uuid_list.append(self.row_instance.export_uuid)
        if self.track_history:
            self.update_export_history(exported_pk_list, export_uuid_list, export_file_contents)
        return self.export_filename

    def fetch_row(self):
        """Returns a one row for the writer."""
        row = []
        value = None
        m2m_row_values = []
        m2m_headers = []
        for field_name in self.field_names:
            value = self.get_row_value_from_attr(self.row_instance, field_name)
            row.append(self.strip_value(value))
        if self.show_all_fields:
            # add m2m fields if show_all_fields -- they are not listed in field_names generated from the model
            m2m_headers, m2m_row_values = self.get_row_values_from_m2m(self.row_instance)
        row.extend(m2m_row_values)
        if self.header_row == self.field_names:
            self.header_row = self.header_row + m2m_headers
        return row

    def get_row_value_from_attr(self, obj, field_name):
        """Gets the row value from the model attr."""
        value = None
        try:
            value = self.get_field_value(obj, field_name)
        except AttributeError:
            if field_name in self.extra_fields:
                value = self.get_row_value_from_query_string(obj, field_name)
        value = value if value is not None else ''
        return unicode(value).encode("utf-8", "replace")

    def get_row_value_from_callable(self, obj, field_name):
        func = self.extra_fields.get(field_name)
        value = func(obj)
        value = value if value is not None else ''
        return unicode(value).encode("utf-8", "replace")

    def get_row_value_from_query_string(self, obj, field_name):
        """Gets the row value by following the query string to related instances."""
        value = None
        if self.extra_fields.get(field_name) or field_name:
            query_string = self.extra_fields.get(field_name) or field_name
            query_list = query_string.split(LOOKUP_SEP)
            # recurse to last relation to get value
            value, _ = self.recurse_on_getattr(obj, query_list)
        value = value if value is not None else ''
        return unicode(value).encode("utf-8", "replace")

    def recurse_on_getattr(self, obj, query_list):
        """ Recurse on result of getattr() with a given query string as a list.

        The query_list is based on a django-style query string split on '__' into
        a list. For example 'field_attr__model_name__field_attr' split to
        ['field_attr', 'model_name', 'field_attr']
        """
        if len(query_list) > 1:
            try:
                return self.recurse_on_getattr(getattr(obj, query_list[0]), query_list[1:])
            except:
                return None, query_list[-1]
        return self.get_field_value(obj, query_list[0], check_for_m2m=False), None

    def get_field_value(self, obj, field_name, check_for_m2m=True):
        """ Gets value of field_name from model instance.

        * If fieldname is an encryption field and only return value based on self.encrypt.
        * If field_name is a m2m, will search for the m2m and return a delimited list of values
        """
        value = None
        for f in obj.__class__._meta.fields:
            if f.name == field_name and issubclass(f.__class__, BaseEncryptedField) and self.encrypt:
                value = '<encrypted>'
            else:
                value = getattr(obj, field_name)
            if not value and check_for_m2m:
                for m2m in obj._meta.many_to_many:
                    if field_name == m2m.name:
                        value = self._m2m_value_delimiter.join(
                            [item.name.encode("utf-8", "replace") for item in getattr(obj, m2m.name).all()])
                        break
        return value

    def get_row_values_from_m2m(self, obj):
        """Look for m2m fields and get the values and return as a delimited string of values."""
        header_row = []
        values_row = []
        for m2m in self.model._meta.many_to_many:
            header_row.append(m2m.name)
            values_row.append(
                self._m2m_value_delimiter.join(
                    [item.name.encode("utf-8", "replace") for item in getattr(obj, m2m.name).all()]))
        return header_row, values_row

    def strip_value(self, string_value):
        """Returns a string cleaned of \n\t\r and double spaces."""
        if self.strip:
            try:
                string_value = string_value.replace(string.whitespace, ' ')
                string_value = ' '.join(string_value.split())
            except AttributeError:
                pass
        return string_value

    def exclude_field_names(self, exclude):
        """Deletes names from the field name and header row lists."""
        if exclude:
            for field_name in exclude:
                try:
                    self.field_names.pop(self.field_names.index(field_name))  # delete from field names
                except ValueError:
                    raise ValueError('Invalid field name in exclude. Got {0}'.format(field_name))
                try:
                    self.header_row.pop(self.header_row.index(field_name))  # delete from header row
                except ValueError:
                    pass

    def insert_defaults_and_reorder_field_names(self):
        """Reorder the field names by moving some to the head and others to the tail of the field list.

        ...note:: Some field "names" in the list are lookups, registered_subject__subject_identifier"""
        head_fields = []
        tail_fields = []
        try:
            for name in HEAD_FIELDS:
                # find a matching field
                if name in self.field_names:
                    head_fields.append(self.field_names.pop(self.field_names.index(name)))
                elif name in [fld[1].split(LOOKUP_SEP)[-1] for fld in self.field_names if isinstance(fld, tuple)]:
                    head_fields.append(self.field_names.pop(self.field_names.index(fld.split(LOOKUP_SEP)[-1])))
        except ValueError:
            pass
        # move tail fields to the end of the list
        for name in TAIL_FIELDS:
            try:
                tail_fields.append(self.field_names.pop(self.field_names.index(name)))
            except ValueError:
                pass
        self.field_names = head_fields + self.field_names + tail_fields

    def update_export_history(self, exported_pk_list, export_uuid_list, export_file_contents):
        self.export_history = ExportHistory.objects.create(
            app_label=self.model._meta.app_label,
            object_name=self.model._meta.object_name,
            pk_list=json.dumps(exported_pk_list),
            export_uuid_list=json.dumps(export_uuid_list),
            exported=True,
            exported_datetime=datetime.now(),
            export_filename=self.export_filename,
            export_file_contents=export_file_contents,
            notification_plan_name=self.notification_plan_name)
