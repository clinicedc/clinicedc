from __future__ import annotations

import shutil
import sys
from pathlib import Path
from tempfile import mkdtemp
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.db import OperationalError
from django.utils import timezone

from edc_model_to_dataframe.model_to_dataframe import ModelToDataframe
from edc_sites.site import sites

from .constants import CSV, STATA_14

if TYPE_CHECKING:
    from datetime import datetime

    from django.contrib.auth.base_user import AbstractBaseUser
    from django.contrib.auth.models import AnonymousUser, User
    from pandas import pd

    from edc_data_manager.models import DataDictionary


class ModelsToFileNothingExportedError(Exception):
    pass


class ModelsToFile:
    """Exports a list of models to individual CSV files and
    adds each to a single zip archive.

    models: a list of model names in label_lower format.
    """

    date_format: str = "%Y-%m-%d %H:%M:%S"
    delimiter: str = "|"
    encoding: str = "utf-8"

    def __init__(
        self,
        *,
        user: User | AbstractBaseUser | AnonymousUser,
        models: list[str],
        site_ids: list[str] | None = None,
        decrypt: bool | None = None,
        archive_to_single_file: bool | None = None,
        export_format: str | int | None = None,
    ):
        self.archive_filename: str | None = None
        self.emailed_datetime: datetime | None = None
        self.emailed_to: str | None = None
        self.exported_filenames: list = []
        self.export_format = export_format or CSV

        self.archive_to_single_file: bool = (
            True if archive_to_single_file is None else archive_to_single_file
        )
        self.decrypt: bool = decrypt or False
        self.models: list[str] = models or []
        self.user = user
        self.site_ids = site_ids or [sites.get_current_site().site_id]
        for site_id in self.site_ids:
            if not sites.get_site_ids_for_user(user=self.user, site_id=site_id):
                self.site_ids = [s for s in self.site_ids if s != site_id]

        # sys.stdout.write(f"Exporting tables for sites: [{','.join(self.site_ids)}]\n")

        self.tmp_folder: Path = Path(mkdtemp())
        formatted_date: str = timezone.now().strftime("%Y%m%d%H%M%S")
        self.working_name = f"{self.user.username}_{formatted_date}"
        (self.tmp_folder / self.working_name).mkdir(parents=False, exist_ok=False)

        for model in self.models:
            if filename := self.model_to_file(model):
                self.exported_filenames.append(filename)
        if not self.exported_filenames:
            raise ModelsToFileNothingExportedError(f"Nothing exported. Got models={models}.")
        if self.archive_to_single_file:
            self.archive_filename = self.create_archive_file()
            sys.stdout.write(f"{self.archive_filename}\n")

    def model_to_file(self, model: str) -> str:
        """Convert model to a dataframe and export as CSV or STATA
        using pandas.Dataframe to_csv() or to_stata().
        """
        filename = None
        try:
            dataframe = ModelToDataframe(
                model=model,
                decrypt=self.decrypt,
                sites=self.site_ids,
                drop_sys_columns=False,
                drop_action_item_columns=True,
                read_frame_verbose=False,
                remove_timezone=False,
            ).dataframe
        except OperationalError as e:
            if "1142" not in str(e):
                raise
            sys.stdout.write(f"Skipping. Got {e}\n")
        else:
            if not dataframe.empty:
                if self.export_format == CSV:
                    path = self.tmp_folder / self.working_name / f"{model}.csv"
                    sys.stdout.write(f"{path}\n")
                    dataframe.to_csv(
                        path_or_buf=path,
                        index=False,
                        encoding=self.encoding,
                        sep=self.delimiter,
                        # date_format=self.date_format,
                    )
                    filename = path.name
                elif self.export_format in [STATA_14]:
                    path = self.tmp_folder / self.working_name / f"{model}.dta"
                    dataframe.to_stata(
                        path,
                        data_label=str(path),
                        version=118,
                        variable_labels=self.stata_variable_labels(dataframe, model=model),
                    )
                    filename = path.name
                else:
                    raise ModelsToFileNothingExportedError(
                        "Invalid file format. Expected CSV or STATA"
                    )
            return filename
        return None

    def create_archive_file(self):
        return shutil.make_archive(
            str(self.tmp_folder / self.working_name),
            "zip",
            root_dir=self.tmp_folder,
            base_dir=self.working_name,
        )

    def stata_variable_labels(self, dataframe: pd.DataFrame, model: str) -> dict[str, str]:
        variable_labels = dict(id="primary key")
        qs = self.data_dictionary_model_cls.objects.values("field_name", "prompt").filter(
            model=model, field_name__in=list(dataframe.columns)
        )
        variable_labels.update({obj.field_name: obj.prompt[:79] for obj in qs})
        return variable_labels

    @property
    def data_dictionary_model_cls(self) -> type[DataDictionary]:
        return django_apps.get_model("edc_data_manager.datadictionary")
