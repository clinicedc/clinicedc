import os
import shutil
import sys

from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from edc_base import get_utcnow
from edc_pdutils import CsvModelExporter
from tempfile import mkdtemp

from .files_archiver import FilesArchiver
from .files_emailer import FilesEmailer, FilesEmailerError
from .models import DataRequest, DataRequestHistory


class NothingToExport(Exception):
    pass


class ArchiveExporterError(Exception):
    pass


class ArchiveExporterEmailError(Exception):
    pass


class ArchiveExporter:

    """Exports a list of models to individual CSV files and
    adds each to a single zip archive OR emails each.
    """

    date_format = '%Y%m%d%H%M%S'
    csv_exporter_cls = CsvModelExporter
    files_emailer_cls = FilesEmailer
    files_archiver_cls = FilesArchiver

    def __init__(self, export_folder=None, date_format=None):
        self.date_format = date_format or self.date_format
        self.export_folder = export_folder or settings.EXPORT_FOLDER

    def export(self, data_request=None, name=None,
               models=None, decrypt=None, user=None,
               archive=None, email_to_user=None,
               **kwargs):
        """Returns a history model instance after exporting
         models to a single zip archive file.

        models: a list of model names in label_lower format.
        """
        if data_request:
            models = data_request.requested_as_list
            decrypt = data_request.decrypt
            user = User.objects.get(username=data_request.user_created)
        else:
            timestamp = datetime.now().strftime('%Y%m%d%H%M')
            data_request = DataRequest.objects.create(
                name=name or f'Data request {timestamp}',
                models='\n'.join(models),
                decrypt=False if decrypt is None else decrypt)
        exported = []
        tmp_folder = mkdtemp()
        for model in models:
            csv_exporter = self.csv_exporter_cls(
                model=model,
                export_folder=tmp_folder,
                decrypt=decrypt, **kwargs)
            exported.append(csv_exporter.to_csv())
        if not exported:
            raise NothingToExport(
                f'Nothing exported. Got models={models}.')
        else:
            summary = [str(x) for x in exported]
            summary.sort()
            exported_datetime = get_utcnow()
            data_request_history = DataRequestHistory.objects.create(
                data_request=data_request,
                exported_datetime=exported_datetime,
                summary='\n'.join(summary),
                user_created=user.username)
            if archive:
                self.files_archiver_cls(
                    export_folder=tmp_folder,
                    user=user,
                    exported_datetime=exported_datetime,
                    data_request_history=data_request_history,
                    date_format=self.date_format)
            if email_to_user:
                try:
                    self.files_emailer_cls(
                        path=tmp_folder,
                        user=user,
                        data_request_history=data_request_history,
                        file_ext='.zip' if archive else '.csv')
                except FilesEmailerError as e:
                    raise ArchiveExporterEmailError(e)
        return data_request_history
