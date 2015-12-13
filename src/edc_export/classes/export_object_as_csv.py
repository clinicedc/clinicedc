import csv
from copy import copy
import json
import os
import string
import numpy as np

from collections import OrderedDict
from datetime import datetime

from django.db.models.constants import LOOKUP_SEP

from ..models import ExportHistory

HEAD_FIELDS = ['export_uuid', 'export_datetime', 'export_change_type', 'unique_key', 'subject_identifier', 'report_datetime']
TAIL_FIELDS = ['hostname_created', 'hostname_modified', 'created', 'modified', 'user_created', 'user_modified', 'revision']


class ExportObjectAsCsv(object):

    def __init__(self, export_filename, fields=None, exclude=None, extra_fields=None,
                 header=True, track_history=None, show_all_fields=True, delimiter=None, encrypt=True,
                 strip=None, target_path=None, notification_plan_name=None, export_datetime=None,
                 dateformat=None):

        self._file_obj = None
        self.field_names = fields
        self.encrypt = encrypt
        self.delimiter = str(delimiter) or ','
        self.header_row = []
        self.include_header_row = header
        self.dateformat = dateformat or '%Y-%m-%d %H:%M'
        self.show_all_fields = show_all_fields
        self.strip = False if strip is False else True
        self.track_history = False if track_history is False else True
        self.notification_plan_name = notification_plan_name
        self.extra_fields = extra_fields or OrderedDict({})
        for field_name in self.field_names:
            self.extra_fields.pop(field_name, None)  # remove items if already listed in field_names
        self.field_names.extend(self.extra_fields.keys() or [])
        self.field_names = list(OrderedDict.fromkeys(self.field_names))  # remove duplicates, maintain order
        self.insert_defaults_and_reorder_field_names()
        self.exclude_field_names(exclude)  # a list of names
        self.header_row = copy(self.field_names)
        export_datetime = export_datetime or datetime.today()
        self.export_filename = export_filename
        self.export_history = None
        self.target_path = target_path

    def write_to_file(self, instances, write_header=True):
        """Writes the export file and returns the file name."""
        # search for unique key in file
        try:
            column = np.loadtxt(
                os.path.join(os.path.expanduser(self.target_path) or '', self.export_filename),
                dtype=str, delimiter=self.delimiter, skiprows=1, usecols=(1,))
            dups = [instance for instance in instances if instance.unique_key in column]
            for dup in dups:
                instances.remove(dup)
                print 'Warning! Not writing record to csv. Duplicate record. Unique Key: {}'.format(dup.unique_key)
        except IOError:
            pass
        with open(os.path.join(os.path.expanduser(self.target_path) or '', self.export_filename), 'a') as f:
            writer = csv.writer(f, delimiter=self.delimiter)
            if write_header:
                writer.writerow(self.header_row)
            for instance in instances:
                row = self.fetch_row(instance)
                writer.writerow(row)
        return self.export_filename

    def fetch_row(self, obj):
        """Returns one row for the writer by getting attrs in the instance."""
        row = []
        for field_name in self.field_names:
            value = getattr(obj, field_name)
            try:
                value = value.strftime(self.dateformat)
            except AttributeError:
                pass
            # except ValueError:
            #    pass   # the datetime strftime() methods require year >= 1900
            if isinstance(value, (list, tuple)):
                value = ';'.join(map(str, value))
            row.append(self.strip_value(value))
        return row

    def strip_value(self, string_value):
        """Returns a string cleaned of \n\t\r and double spaces."""
        if self.strip:
            try:
                string_value = string_value.replace(string.whitespace, ' ')
                string_value = ' '.join(string_value.split())
            except AttributeError:
                pass
            except TypeError:
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
            app_label='object',
            object_name=self.object_name,
            pk_list=json.dumps(exported_pk_list),
            export_uuid_list=json.dumps(export_uuid_list),
            exported=True,
            exported_datetime=datetime.now(),
            export_filename=self.export_filename,
            export_file_contents=export_file_contents,
            notification_plan_name=self.notification_plan_name,
            )

    def update_export_transaction(self, instance):
        pass
