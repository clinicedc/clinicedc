import os
import shutil
import sys

from django.apps import apps as django_apps
from django.conf import settings
from edc_base.utils import get_utcnow
from tempfile import mkdtemp

from .csv_exporters import CsvModelExporter


class NothingToExport(Exception):
    pass


class ArchiveExporter:

    """Exports a list of models to individual CSV files and
    adds each to a single zip archive.
    """

    date_format = '%Y%m%d%H%M%S'
    history_model = 'edc_pdutils.datarequest'
    csv_exporter_cls = CsvModelExporter

    def __init__(self, export_folder=None, date_format=None):
        self.date_format = date_format or self.date_format
        self.export_folder = export_folder or settings.EXPORT_FOLDER
        self.history_model_cls = django_apps.get_model(self.history_model)

    def export_to_archive(self, models=None, decrypt=None, user=None, **kwargs):
        """Returns a history model instance after exporting
         models to a single zip archive file.

        models: a list of model names in label_lower format.
        """
        history = None
        exported = []
        tmp_folder = mkdtemp()
        user = user or 'unknown_user'
        for model in models:
            print(model)
            csv_exporter = self.csv_exporter_cls(
                model=model,
                export_folder=tmp_folder,
                decrypt=decrypt, **kwargs)
            exported.append(csv_exporter.to_csv())
        if not exported:
            raise NothingToExport(
                f'Nothing exported. Got models={models}.')
        else:
            archive_filename = self._archive(tmp_folder=tmp_folder, user=user)
            exported_datetime = get_utcnow()
            history = self.history_model_cls.objects.create(
                requested='\n'.join(models),
                decrypt=False if decrypt is None else decrypt,
                exported_datetime=exported_datetime,
                archive_filename=archive_filename,
                user_created=user,
                exported=True)
            sys.stdout.write(
                f'\nExported archive to {history.archive_filename}.\n')
        return history

    def _archive(self, tmp_folder=None, exported_datetime=None, user=None):
        """Returns the archive zip filename after calling make_archive.
        """
        exported_datetime = exported_datetime or get_utcnow()
        formatted_date = exported_datetime.strftime(self.date_format)
        return shutil.make_archive(
            os.path.join(self.export_folder, f'{user}_{formatted_date}'), 'zip', tmp_folder)
