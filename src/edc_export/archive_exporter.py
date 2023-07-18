from __future__ import annotations

from tempfile import mkdtemp
from typing import TYPE_CHECKING, Type

from edc_pdutils import CsvModelExporter
from edc_sites.get_sites_from_user import get_sites_from_user
from edc_utils import get_utcnow

from .files_archiver import FilesArchiver
from .files_emailer import FilesEmailer, FilesEmailerError

if TYPE_CHECKING:
    from datetime import datetime

    from django.contrib.auth.models import User


class ArchiveExporterNothingExported(Exception):
    pass


class ArchiveExporterEmailError(Exception):
    pass


class ArchiveExporter:

    """Exports a list of models to individual CSV files and
    adds each to a single zip archive OR emails each.

    models: a list of model names in label_lower format.
    """

    date_format: str = "%Y%m%d%H%M%S"
    csv_exporter_cls: Type[CsvModelExporter] = CsvModelExporter
    files_emailer_cls: Type[FilesEmailer] = FilesEmailer
    files_archiver_cls: Type[FilesArchiver] = FilesArchiver

    def __init__(
        self,
        models: list[str] = None,
        decrypt: bool | None = None,
        user: User = None,
        archive: bool | None = None,
        email_to_user: bool | None = None,
        **kwargs,
    ):
        models: list[str] = models or []
        self.archive_filename: str | None = None
        self.exported: list = []
        self.emailed_to: str | None = None
        self.emailed_datetime: datetime | None = None
        self.exported_datetime: datetime | None = None
        tmp_folder: str = mkdtemp()
        for model in models:
            csv_exporter = self.csv_exporter_cls(
                model=model,
                export_folder=tmp_folder,
                decrypt=decrypt,
                sites=get_sites_from_user(user),
                **kwargs,
            )
            self.exported.append(csv_exporter.to_csv())
        if not self.exported:
            raise ArchiveExporterNothingExported(f"Nothing exported. Got models={models}.")
        else:
            if archive:
                archiver = self.files_archiver_cls(
                    path=tmp_folder,
                    user=user,
                    exported_datetime=self.exported_datetime,
                    date_format=self.date_format,
                )
                self.archive_filename = archiver.archive_filename
                self.exported_datetime = archiver.exported_datetime
            if email_to_user:
                summary = [str(x) for x in self.exported]
                summary.sort()
                try:
                    self.files_emailer_cls(
                        path=tmp_folder,
                        user=user,
                        file_ext=".zip" if archive else ".csv",
                        summary="\n".join(summary),
                    )
                except FilesEmailerError as e:
                    raise ArchiveExporterEmailError(e)
                else:
                    self.emailed_to = user.email
                    self.emailed_datetime = get_utcnow()
                    self.exported_datetime = self.exported_datetime or self.emailed_datetime
