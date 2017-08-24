import os
import sys

from django.apps import apps as django_apps
from django.core.management.color import color_style
from edc_base.utils import get_utcnow

app_config = django_apps.get_app_config('edc_pdutils')
style = color_style()


class CsvExporterExportFolder(Exception):
    pass


class CsvExporter:

    delimiter = '|'
    encoding = 'utf-8'
    export_folder = app_config.export_folder
    csv_date_format = None

    def __init__(self, export_folder=None, **kwargs):
        if export_folder:
            self.export_folder = export_folder
        if not self.export_folder or not os.path.exists(self.export_folder):
            raise CsvExporterExportFolder(
                f'Invalid export folder. Got {self.export_folder}')

    def to_csv(self, label=None, dataframe=None, include_index=None, exists_ok=None):
        sys.stdout.write(label + '\r')
        path = None
        if not dataframe.empty:
            path = os.path.join(self.export_folder,
                                self.get_filename(label=label))
            if os.path.exists(path) and not exists_ok:
                sys.stdout.write(style.ERROR(
                    f'File \'{path}\' exists! Exporting {label}.\n'))
            else:
                sys.stdout.write(f'( ) {label} ...     \r')
                dataframe.to_csv(
                    columns=dataframe.columns,
                    path_or_buf=path,
                    index=include_index,
                    encoding=self.encoding,
                    sep=self.delimiter,
                    date_format=self.csv_date_format)
                sys.stdout.write(f'(*) {label}           \n')
        else:
            sys.stdout.write(f'(?) {label} empty  \n')
        return path

    def get_filename(self, label=None):
        """Returns a CSV filename based on the timestamp.
        """
        dt = get_utcnow()
        label = label.replace('-', '_')
        formatted_date = dt.strftime('%Y%m%d%H%M%S')
        return f'{label}_{formatted_date}.csv'
