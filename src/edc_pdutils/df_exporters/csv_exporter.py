from __future__ import annotations

import os
import sys

import pandas as pd
from django.apps import apps as django_apps
from django.conf import settings
from django.core.management.color import color_style
from django.db.models import QuerySet
from edc_export.utils import get_export_folder
from edc_utils import get_utcnow

from ..site_values_mappings import site_values_mappings
from ..utils import get_model_from_table_name

style = color_style()


class ExporterExportFolder(Exception):
    pass


class ExporterInvalidExportFormat(Exception):
    pass


class ExporterFileExists(Exception):
    pass


class Exported:
    def __init__(
        self, path: str = None, model_name: str = None, record_count: int | None = None
    ):
        self.path = path
        self.model_name = model_name
        self.record_count = record_count

    def __repr__(self):
        return f"{self.__class__.__name__}(model_name={self.model_name})"

    def __str__(self):
        return f"{self.model_name} {self.record_count}"


class CsvExporter:
    date_format: str | None = None
    delimiter: str = "|"
    encoding: str = "utf-8"
    file_exists_ok: bool = False
    index: bool = False
    sort_by: list | tuple | str | None = None

    def __init__(
        self,
        model_name: str | None = None,
        table_name: str | None = None,
        data_label: str | None = None,
        sort_by: list | tuple | str | None = None,
        export_folder: str = None,
        delimiter: str | None = None,
        date_format: str | None = None,
        index: bool | None = None,
        verbose=None,
    ):
        self.delimiter = delimiter or self.delimiter
        self.date_format = date_format or self.date_format
        self.index = index or self.index
        self.sort_by = sort_by or self.sort_by
        if self.sort_by and not isinstance(self.sort_by, (list, tuple)):
            self.sort_by = [self.sort_by]
        self.export_folder = export_folder or get_export_folder()
        self.verbose = verbose
        if not self.export_folder:
            raise ExporterExportFolder("Invalid export folder. Got None")
        if not os.path.exists(self.export_folder):
            raise ExporterExportFolder(f"Invalid export folder. Got {self.export_folder}")
        if not model_name:
            self.model_name = get_model_from_table_name(table_name)
        else:
            self.model_name = model_name
        self.model_cls = django_apps.get_model(self.model_name)
        self.data_label = data_label or model_name or table_name

    def to_format(self, export_format, dataframe=None, export_folder=None, **kwargs):
        """Returns the full path of the written CSV file if the
        dataframe is exported otherwise None.

        Note: You could also just do:

            dataframe.to_csv(path_or_buf=path, **self.csv_options)

            to suppress stdout messages.
        """
        path = None
        record_count = 0
        if self.verbose:
            sys.stdout.write(self.model_name + "\r")
        if export_folder:
            self.export_folder = export_folder
        if not dataframe.empty:
            path = self.get_path()
            if self.sort_by:
                dataframe.sort_values(by=self.sort_by, inplace=True)
            if self.verbose:
                sys.stdout.write(f"( ) {self.model_name} ...     \r")
            if export_format == "csv":
                path = ".".join([path, "csv"])
                dataframe.to_csv(path_or_buf=path, **self.csv_options)
            elif export_format == "stata":
                path = ".".join([path, "dta"])
                dataframe.to_stata(path=path, **self.stata_options, **kwargs)
            else:
                raise ExporterInvalidExportFormat(
                    f"Invalid export format. Got {export_format}"
                )
            record_count = len(dataframe)
            if self.verbose:
                sys.stdout.write(
                    f'({style.SUCCESS("*")}) {self.model_name} {record_count}       \n'
                )
        else:
            if self.verbose:
                sys.stdout.write(f"(?) {self.model_name} empty  \n")
        return Exported(path, self.model_name, record_count)

    def to_csv(self, dataframe=None, export_folder=None):
        """Returns the full path of the written CSV file if the
        dataframe is exported otherwise None.

        Note: You could also just do:

            dataframe.to_csv(path_or_buf=path, **self.csv_options)

            to suppress stdout messages.
        """
        return self.to_format("csv", dataframe=dataframe, export_folder=export_folder)

    def to_stata(self, dataframe=None, export_folder=None):
        """Returns the full path of the written STATA file if the
        dataframe is exported otherwise None.
        """
        opts = dict(
            dataframe=dataframe,
            export_folder=export_folder,
            variable_labels=self.stata_variable_labels(dataframe),
        )
        return self.to_format("stata", **opts)

    @property
    def csv_options(self):
        """Returns default options for dataframe.to_csv()."""
        return dict(
            index=self.index,
            encoding=self.encoding,
            sep=self.delimiter,
            date_format=self.date_format,
        )

    @property
    def stata_options(self):
        """Returns default options for dataframe.to_stata()."""
        return dict(
            data_label=f"{self.data_label}.dta",
            version=118,
        )

    def get_path(self):
        """Returns a full path and filename."""
        path = os.path.join(self.export_folder, self.filename)
        if os.path.exists(path) and not self.file_exists_ok:
            raise ExporterFileExists(
                f"File '{path}' exists! Not exporting {self.model_name}.\n"
            )
        return path

    @property
    def filename(self):
        """Returns a CSV filename based on the timestamp."""
        try:
            timestamp_format = settings.EXPORT_FILENAME_TIMESTAMP_FORMAT
        except AttributeError:
            timestamp_format = "%Y%m%d%H%M%S"
        if not timestamp_format:
            suffix = ""
        else:
            suffix = f"_{get_utcnow().strftime(timestamp_format)}"
        prefix = self.model_name.replace("-", "_").replace(".", "_")
        return f"{prefix}{suffix}"

    def stata_variable_labels(self, dataframe: pd.DataFrame) -> dict[str, str]:
        return {obj.field_name: obj.prompt[:79] for obj in self.data_dictionary_qs(dataframe)}

    def stata_value_labels(self, dataframe: pd.DataFrame):
        commands = []
        choices = {}
        for field_cls in self.model_cls._meta.get_fields():
            if field_cls.get_internal_type() == "CharField":
                if field_cls.choices:
                    responses = []
                    for tpl in field_cls.choices:
                        if mapped_choice := site_values_mappings.get_by_choices(tpl):
                            responses.append([mapped_choice[0], mapped_choice[1]])
                        else:
                            responses.append([tpl[0], tpl[1]])
                    choices.update({field_cls.name: responses})
        for fname, responses in choices.items():
            labels = []
            if fname in list(dataframe.columns):
                for stored, displayed in responses:
                    labels.append(f'"{stored}" "{displayed}"')
                commands.append(f'label define {fname}l {" ".join(labels)}')
                commands.append(f"encode {fname}, generate({fname}_encoded) {fname}l")
                commands.append(f"ren {fname} {fname}_edc")
                commands.append(f"ren {fname}_encoded {fname}")
                commands.append("")
        with open(f"{self.get_path()}.do", "w") as f:
            for command in commands:
                f.write(f"{command}\n")
        return commands

    def data_dictionary_qs(self, dataframe: pd.DataFrame) -> QuerySet:
        data_dictionary_model_cls = django_apps.get_model("edc_data_manager.DataDictionary")
        return data_dictionary_model_cls.objects.filter(
            model=self.model_name, field_name__in=list(dataframe.columns)
        )
