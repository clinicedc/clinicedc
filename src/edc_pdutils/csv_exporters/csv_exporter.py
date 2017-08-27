import os
import sys

from django.apps import apps as django_apps
from django.core.management.color import color_style
from edc_base.utils import get_utcnow

app_config = django_apps.get_app_config('edc_pdutils')
style = color_style()


class CsvExporterExportFolder(Exception):
    pass


class CsvExporterFileExists(Exception):
    pass


class CsvExporter:

    delimiter = '|'
    encoding = 'utf-8'
    export_folder = app_config.export_folder
    include_index = False
    file_exists_ok = False
    csv_date_format = None
    sort_by = None

    def __init__(self, data_label=None):
        self._filename = None
        if not os.path.exists(self.export_folder):
            raise CsvExporterExportFolder(
                f'Invalid export folder. Got {self.export_folder}')
        self.data_label = data_label
        self.path = os.path.join(self.export_folder, self.filename)
        if os.path.exists(self.path) and not self.file_exists_ok:
            raise CsvExporterFileExists(
                f'File \'{self.path}\' exists! Not exporting {self.data_label}.\n')
        self.include_index = False

    def to_csv(self, dataframe=None):
        """Returns the full path of the written CSV file or None.

        Note: You could also just do dataframe.to_csv(**self.csv_options)
              to suppress stdout messages.
        """
        sys.stdout.write(self.data_label + '\r')
        if not dataframe.empty:
            if self.sort_by:
                dataframe.sort_values(self.sort_by, inplace=True)
            sys.stdout.write(f'( ) {self.data_label} ...     \r')
            dataframe.to_csv(**self.csv_options)
            sys.stdout.write(f'(*) {self.data_label}           \n')
        else:
            sys.stdout.write(f'(?) {self.data_label} empty  \n')
        return self.path if not dataframe.empty else None

    @property
    def csv_options(self):
        """Returns default options for dataframe.to_csv().
        """
        return dict(
            path_or_buf=self.path,
            index=self.include_index,
            encoding=self.encoding,
            sep=self.delimiter,
            date_format=self.csv_date_format)

    @property
    def filename(self):
        """Returns a CSV filename based on the timestamp.
        """
        if not self._filename:
            dt = get_utcnow()
            prefix = self.data_label.replace('-', '_')
            formatted_date = dt.strftime('%Y%m%d%H%M%S')
            self._filename = f'{prefix}_{formatted_date}.csv'
        return self._filename
