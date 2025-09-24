from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from django.core.management.color import color_style

from edc_model_to_dataframe.model_to_dataframe import ModelToDataframe

from .csv_exporter import CsvExporter

if TYPE_CHECKING:
    from django.db.models import QuerySet

style = color_style()


class CsvModelExporter:
    df_maker_cls = ModelToDataframe
    csv_exporter_cls = CsvExporter

    def __init__(
        self,
        model: str | None = None,
        queryset: QuerySet | None = None,
        decrypt: bool | None = None,
        sort_by: list | tuple | str | None = None,
        export_folder: Path | None = None,
        site_ids: list[int] | None = None,
        **kwargs,
    ):
        self.model = model or queryset.model._meta.label_lower
        self.export_folder = export_folder
        self.df_maker = self.df_maker_cls(
            model=model,
            queryset=queryset,
            decrypt=decrypt,
            sites=site_ids or [],
            **kwargs,
        )
        self.csv_exporter = self.csv_exporter_cls(
            model_name=self.model,
            sort_by=sort_by,
            export_folder=export_folder,
            **kwargs,
        )

    def to_csv(self):
        dataframe = self.df_maker.dataframe
        return self.csv_exporter.to_csv(dataframe=dataframe, export_folder=self.export_folder)

    def to_stata(self):
        dataframe = self.df_maker.dataframe
        return self.csv_exporter.to_stata(
            dataframe=dataframe, export_folder=self.export_folder
        )
