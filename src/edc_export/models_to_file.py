from __future__ import annotations

import shutil
import sys
from pathlib import Path
from tempfile import mkdtemp
from typing import TYPE_CHECKING

import pandas as pd
from django.apps import apps as django_apps
from django.db import OperationalError
from django.utils import timezone
from tabulate import tabulate
from tqdm import tqdm

from edc_model_to_dataframe.model_to_dataframe import ModelToDataframe
from edc_sites.site import sites

from .constants import CSV, STATA_14, STATA_15

if TYPE_CHECKING:
    from datetime import datetime

    from django.contrib.auth.base_user import AbstractBaseUser
    from django.contrib.auth.models import AnonymousUser, User
    from pandas import pd

    from edc_data_manager.models import DataDictionary


class ModelsToFileError(Exception):
    pass


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
        export_folder: Path | None = None,
        site_ids: list[int] | None = None,
        decrypt: bool | None = None,
        archive_to_single_file: bool | None = None,
        export_format: str | int | None = None,
        use_simple_filename: bool | None = None,
        date_format: str | None = None,
    ):
        self.archive_filename: str | None = None
        self.emailed_datetime: datetime | None = None
        self.emailed_to: str | None = None
        self.exported_filenames: list = []
        self.export_history = dict(model=[], rows=[])
        self.export_format = export_format or CSV
        if export_format not in [CSV, STATA_14, STATA_15]:
            raise ModelsToFileError(
                f"Invalid export format. Expected one of {[CSV, STATA_14, STATA_15]}. "
                f"Got {export_format}"
            )
        self.use_simple_filename = use_simple_filename
        self.date_format = date_format or self.date_format

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

        if export_folder and not export_folder.exists():
            raise ModelsToFileError(f"Export folder does not exist. Got {export_folder}.")
        self.export_folder: Path = export_folder if export_folder else Path(mkdtemp())
        formatted_date: str = timezone.now().strftime("%Y%m%d%H%M%S")
        self.sub_folder = (
            f"{self.user.username}_{'csv' if export_format == CSV else 'stata'}_"
            f"{formatted_date}"
        )
        (self.export_folder / self.sub_folder).mkdir(parents=False, exist_ok=False)

        for model in tqdm(self.models, total=len(self.models)):
            if filename := self.model_to_file(model):
                self.exported_filenames.append(filename)
        if not self.exported_filenames:
            raise ModelsToFileNothingExportedError(f"Nothing exported. Got models={models}.")
        if self.export_history:
            with (self.export_folder / self.sub_folder / "README.txt").open("w") as f:
                f.write("\nExport Summary\n")
                f.write(
                    tabulate(
                        pd.DataFrame(data=self.export_history)
                        .sort_values("model")
                        .reset_index(drop=True),
                        tablefmt="fancy_grid",
                        headers="keys",
                        showindex=False,
                    )
                )
                f.write("\n")
                f.write(f"{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        if self.archive_to_single_file:
            self.archive_filename = self.create_archive_file()
            sys.stdout.write(f"{self.archive_filename}\n")

    def model_to_file(self, model: str) -> str | None:
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
                remove_timezone=True,
            ).dataframe
        except OperationalError as e:
            if "1142" not in str(e):
                raise
            sys.stdout.write(f"Skipping. Got {e}\n")
        else:
            if not dataframe.empty:
                self.export_history["model"].append(model)
                self.export_history["rows"].append(len(dataframe))
                fname = (
                    model.split(".")[-1:][0].upper() if self.use_simple_filename else model
                ).replace(".", "_")
                if self.export_format == CSV:
                    path = self.export_folder / self.sub_folder / f"{fname}.csv"
                    dataframe.to_csv(
                        path_or_buf=path,
                        index=False,
                        encoding=self.encoding,
                        sep=self.delimiter,
                        date_format=self.date_format,
                    )
                elif self.export_format in [STATA_14, STATA_15]:
                    path = self.export_folder / self.sub_folder / f"{fname}.dta"
                    dataframe.to_stata(
                        path,
                        data_label=str(path),
                        version=118,
                        variable_labels=self.stata_variable_labels(dataframe, model=model),
                        write_index=False,
                    )
                else:
                    raise ModelsToFileNothingExportedError(
                        "Invalid file format. Expected CSV or STATA"
                    )
                filename = path.name
            return filename
        return None

    def get_filename_without_ext(self, model_name: str) -> str:
        return (
            model_name.split("_")[-1:][0].upper() if self.use_simple_filename else model_name
        )

    def create_archive_file(self):
        return shutil.make_archive(
            str(self.export_folder / self.sub_folder),
            "zip",
            root_dir=self.export_folder,
            base_dir=self.sub_folder,
        )

    def stata_variable_labels(self, dataframe: pd.DataFrame, model: str) -> dict[str, str]:
        variable_labels = dict(id="primary key")
        qs = self.data_dictionary_model_cls.objects.values("field_name", "prompt").filter(
            model=model, field_name__in=list(dataframe.columns)
        )
        variable_labels.update({obj.get("field_name"): obj.get("prompt")[:79] for obj in qs})
        return variable_labels

    @property
    def data_dictionary_model_cls(self) -> type[DataDictionary]:
        return django_apps.get_model("edc_data_manager.datadictionary")
