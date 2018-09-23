from edc_base import get_utcnow
from edc_pdutils import CsvModelExporter
from tempfile import mkdtemp

from .files_archiver import FilesArchiver
from .files_emailer import FilesEmailer, FilesEmailerError


class ArchiveExporterNothingExported(Exception):
    pass


class ArchiveExporterEmailError(Exception):
    pass


class ArchiveExporter:

    """Exports a list of models to individual CSV files and
    adds each to a single zip archive OR emails each.

    models: a list of model names in label_lower format.
    """

    date_format = '%Y%m%d%H%M%S'
    csv_exporter_cls = CsvModelExporter
    files_emailer_cls = FilesEmailer
    files_archiver_cls = FilesArchiver

    def __init__(self, models=None, decrypt=None, user=None,
                 archive=None, email_to_user=None, **kwargs):
        models = models or []
        self.archive_filename = None
        self.exported = []
        self.emailed_to = None
        self.emailed_datetime = None
        self.exported_datetime = None
        tmp_folder = mkdtemp()
        for model in models:
            csv_exporter = self.csv_exporter_cls(
                model=model,
                export_folder=tmp_folder,
                decrypt=decrypt, **kwargs)
            self.exported.append(csv_exporter.to_csv())
        if not self.exported:
            raise ArchiveExporterNothingExported(
                f'Nothing exported. Got models={models}.')
        else:
            if archive:
                archiver = self.files_archiver_cls(
                    path=tmp_folder,
                    user=user,
                    exported_datetime=self.exported_datetime,
                    date_format=self.date_format)
                self.archive_filename = archiver.archive_filename
                self.exported_datetime = archiver.exported_datetime
            if email_to_user:
                summary = [str(x) for x in self.exported]
                summary.sort()
                try:
                    self.files_emailer_cls(
                        path=tmp_folder,
                        user=user,
                        file_ext='.zip' if archive else '.csv',
                        summary='\n'.join(summary))
                except FilesEmailerError as e:
                    raise ArchiveExporterEmailError(e)
                else:
                    self.emailed_to = user.email
                    self.emailed_datetime = get_utcnow()
                    self.exported_datetime = (
                        self.exported_datetime or self.emailed_datetime)
