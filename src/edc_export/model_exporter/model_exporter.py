import csv
import os
import uuid

from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_base.utils import get_utcnow
from edc_pdutils import ValueGetter

from .file_history_updater import FileHistoryUpdater
from .object_history_helpers import ObjectHistoryHelper

app_config = django_apps.get_app_config('edc_export')


class ModelExporterError(Exception):
    pass


class ModelExporterInvalidLookup(Exception):
    pass


class ModelExporterUnknownField(ValidationError):
    pass


class AdditionalValues:
    def __init__(self, export_datetime=None):
        self.export_uuid = str(uuid.uuid4())
        self.export_datetime = export_datetime
        self.timestamp = self.export_datetime.strftime('%Y%m%d%H%M%S')
        self.export_change_type = None


class ModelExporter(object):

    delimiter = '|'
    file_history_updater_cls = FileHistoryUpdater
    object_history_helper_cls = ObjectHistoryHelper
    value_getter_cls = ValueGetter
    additional_values_cls = AdditionalValues
    export_folder = app_config.export_folder

    export_fields = [
        'export_uuid', 'timestamp', 'export_datetime', 'export_change_type']
    required_fields = ['subject_identifier', 'report_datetime']
    audit_fields = [
        'hostname_created', 'hostname_modified', 'created',
        'modified', 'user_created', 'user_modified', 'revision']

    def __init__(self, queryset=None, model=None, field_names=None,
                 exclude_field_names=None, lookups=None,
                 exclude_m2m=None, encrypt=None):
        self._model = model
        self._model_cls = None
        self.encrypt = True if encrypt is None else encrypt
        self.exclude_m2m = exclude_m2m
        self.lookups = lookups or {}
        self.queryset = queryset
        self.row = None
        self.row_instance = None

        if field_names:
            self.field_names = field_names
        else:
            self.field_names = [f.name for f in self.model_cls._meta.fields]
            if not exclude_m2m:
                for m2m in self.model_cls._meta.many_to_many:
                    self.field_names.append(m2m.name)
            if exclude_field_names:
                for f in self.field_names:
                    if f in exclude_field_names:
                        self.field_names.pop(self.field_names.index(f))

        for f in self.field_names:
            if f in self.export_fields or f in self.audit_fields or f in self.required_fields:
                self.field_names.pop(self.field_names.index(f))
        self.field_names = (self.export_fields
                            + self.required_fields
                            + self.field_names
                            + self.audit_fields)

    @property
    def model_cls(self):
        if not self._model_cls:
            try:
                self.queryset.count()
            except AttributeError:
                self._model_cls = django_apps.get_model(self._model)
            else:
                self._model_cls = self.queryset.model
        return self._model_cls

    def export(self, queryset=None):
        """Writes the export file and returns the file name.
        """
        self.queryset = queryset or self.queryset
        exported_datetime = get_utcnow()
        filename = self.get_filename(exported_datetime)
        path = os.path.join(self.export_folder, filename)
        with open(path, 'w') as f:
            csv_writer = csv.DictWriter(
                f, fieldnames=self.field_names, delimiter=self.delimiter)
            csv_writer.writeheader()
            for model_obj in self.queryset:
                object_helper = self.object_history_helper_cls(
                    model_obj=model_obj, create=True)
                objects = object_helper.get_not_exported()
                for obj in objects:
                    row = self.prepare_row(
                        model_obj=model_obj,
                        exported_datetime=exported_datetime,
                        export_change_type=obj.export_change_type)
                    csv_writer.writerow(row)
                object_helper.update_as_exported(
                    objects=objects, exported_datetime=exported_datetime)
        file_history_updater = self.file_history_updater_cls(
            path=path,
            delimiter=self.delimiter,
            model=self.model_cls._meta.label_lower,
            filename=filename)
        file_history_updater.update()
        return path

    def prepare_row(self, model_obj=None, exported_datetime=None, export_change_type=None):
        """Returns one row for the CSV writer.
        """
        additional_values = self.additional_values_cls(
            export_datetime=exported_datetime)
        row = {}
        for field_name in self.field_names:
            value_getter = self.value_getter_cls(
                field_name=field_name,
                model_obj=model_obj,
                additional_values=additional_values,
                lookups=self.lookups,
                encrypt=self.encrypt)
            row.update({field_name: value_getter.value})
            row['exported'] = True
            row['exported_datetime'] = exported_datetime
            row['timestamp'] = exported_datetime.strftime('%Y%m%d%H%M%S')
            row['export_uuid'] = model_obj.export_uuid
            row['export_change_type'] = export_change_type
        return row

    def get_filename(self, exported_datetime=None):
        """Returns a CSV filename using the model label lower
        and the exported date.
        """
        formatted_model = self.model_cls._meta.label_lower.replace(".", "_")
        formatted_date = exported_datetime.strftime('%Y%m%d%H%M%S')
        return f'{formatted_model}_{formatted_date}.csv'
