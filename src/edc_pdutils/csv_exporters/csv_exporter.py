import os
import sys

from django.core.management.color import color_style
from edc_base import get_utcnow


style = color_style()


class CsvExporterExportFolder(Exception):
    pass


class CsvExporterFileExists(Exception):
    pass


class Exported:
    def __init__(self, path=None, data_label=None, record_count=None):
        self.path = path
        self.data_label = data_label
        self.record_count = record_count

    def __repr__(self):
        return f'{self.__class__.__name__}(data_label={self.data_label})'

    def __str__(self):
        return f'{self.data_label} {self.record_count}'


class CsvExporter:

    delimiter = '|'
    encoding = 'utf-8'
    export_folder = None
    index = False
    file_exists_ok = False
    date_format = None
    sort_by = None

    def __init__(self, data_label=None, sort_by=None, export_folder=None,
                 delimiter=None, date_format=None, index=None, **kwargs):
        self.delimiter = delimiter or self.delimiter
        self.date_format = date_format or self.date_format
        self.index = index or self.index
        self.sort_by = sort_by or self.sort_by
        self.export_folder = export_folder or self.export_folder
        if not os.path.exists(self.export_folder):
            raise CsvExporterExportFolder(
                f'Invalid export folder. Got {self.export_folder}')
        self.data_label = data_label

    def to_csv(self, dataframe=None, export_folder=None):
        """Returns the full path of the written CSV file if the
        dataframe is exported otherwise None.

        Note: You could also just do:
            >>> dataframe.to_csv(path_or_buf=path, **self.csv_options)
            to suppress stdout messages.
        """
        path = None
        record_count = 0
        sys.stdout.write(self.data_label + '\r')
        if export_folder:
            self.export_folder = export_folder
        if not dataframe.empty:
            path = self.get_path()
            if self.sort_by:
                dataframe.sort_values(self.sort_by, inplace=True)
            sys.stdout.write(f'( ) {self.data_label} ...     \r')
            dataframe.to_csv(path_or_buf=path, **self.csv_options)
            record_count = len(dataframe)
            sys.stdout.write(
                f'({style.SUCCESS("*")}) {self.data_label} {record_count}       \n')
        else:
            sys.stdout.write(f'(?) {self.data_label} empty  \n')
        return Exported(path, self.data_label, record_count)

    @property
    def csv_options(self):
        """Returns default options for dataframe.to_csv().
        """
        return dict(
            index=self.index,
            encoding=self.encoding,
            sep=self.delimiter,
            date_format=self.date_format)

    def get_path(self):
        """Returns a full path and filename.
        """
        path = os.path.join(self.export_folder, self.filename)
        if os.path.exists(path) and not self.file_exists_ok:
            raise CsvExporterFileExists(
                f'File \'{path}\' exists! Not exporting {self.data_label}.\n')
        return path

    @property
    def filename(self):
        """Returns a CSV filename based on the timestamp.
        """
        dt = get_utcnow()
        prefix = self.data_label.replace('-', '_')
        formatted_date = dt.strftime('%Y%m%d%H%M%S')
        return f'{prefix}_{formatted_date}.csv'
