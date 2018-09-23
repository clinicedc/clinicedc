import os
import shutil
import sys

from django.conf import settings
from edc_base import get_utcnow


class FilesArchiver:
    """Archives a folder of CSV files using make_archive.
    """

    def __init__(self, export_folder=None, exported_datetime=None, user=None,
                 data_request_history=None, date_format=None):
        export_folder = export_folder or settings.EXPORT_FOLDER
        exported_datetime = exported_datetime or get_utcnow()
        formatted_date = exported_datetime.strftime(date_format)
        self.archive_filename = shutil.make_archive(
            os.path.join(
                export_folder, f'{user.username}_{formatted_date}'), 'zip', export_folder)
        if data_request_history:
            data_request_history.archive_filename = self.archive_filename
            data_request_history.save()
        sys.stdout.write(
            f'\nExported archive to {self.archive_filename}.\n')
