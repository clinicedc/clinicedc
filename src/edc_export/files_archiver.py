import os
import shutil
import sys

from edc_utils import get_utcnow


class FilesArchiver:
    """Archives a folder of CSV files using make_archive.
    """

    def __init__(
        self,
        path=None,
        exported_datetime=None,
        user=None,
        date_format=None,
        verbose=None,
    ):
        self.exported_datetime = exported_datetime or get_utcnow()
        formatted_date = self.exported_datetime.strftime(date_format)
        self.archive_filename = shutil.make_archive(
            os.path.join(path, f"{user.username}_{formatted_date}"), "zip", path
        )
        if verbose:
            sys.stdout.write(f"\nExported archive to {self.archive_filename}.\n")
