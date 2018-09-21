import os
import shutil
import sys

from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from edc_base import get_utcnow
from edc_pdutils import CsvModelExporter
from tempfile import mkdtemp

from .files_emailer import FilesEmailer
from .models import DataRequest, DataRequestHistory


class NothingToExport(Exception):
    pass


class ArchiveExporterError(Exception):
    pass


class ArchiveExporter:

    """Exports a list of models to individual CSV files and
    adds each to a single zip archive.
    """

    date_format = '%Y%m%d%H%M%S'
    csv_exporter_cls = CsvModelExporter
    files_emailer_cls = FilesEmailer

    def __init__(self, export_folder=None, date_format=None, email_to_user=None):
        self.date_format = date_format or self.date_format
        self.export_folder = export_folder or settings.EXPORT_FOLDER
        self.email_to_user = email_to_user

    def export_to_archive(self, data_request=None, name=None,
                          models=None, decrypt=None, user=None, **kwargs):
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
            data_request_history = DataRequestHistory.objects.create(
                data_request=data_request,
                exported_datetime=get_utcnow(),
                summary='\n'.join(summary),
                user_created=user.username)
            if self.email_to_user:
                self.files_emailer_cls(
                    path=tmp_folder,
                    user=user,
                    data_request_history=data_request_history)
            else:
                archive_filename = self._archive(
                    tmp_folder=tmp_folder, user=user)
                data_request_history.archive_filename = archive_filename
                data_request_history.save()
                sys.stdout.write(
                    f'\nExported archive to {data_request_history.archive_filename}.\n')
        return data_request_history

    def _archive(self, tmp_folder=None, exported_datetime=None, user=None):
        """Returns the archive zip filename after calling make_archive.
        """
        exported_datetime = exported_datetime or get_utcnow()
        formatted_date = exported_datetime.strftime(self.date_format)
        export_folder = tmp_folder if self.email_to_user else self.export_folder
        return shutil.make_archive(
            os.path.join(
                export_folder, f'{user.username}_{formatted_date}'), 'zip', tmp_folder)
