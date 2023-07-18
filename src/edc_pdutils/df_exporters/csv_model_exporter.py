from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.management.color import color_style

from ..model_to_dataframe import ModelToDataframe
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
        export_folder: str | None = None,
        sites: list[int] | None = None,
        **kwargs,
    ):
        self.model = model or queryset.model._meta.label_lower
        self.df_maker = self.df_maker_cls(
            model=model, queryset=queryset, decrypt=decrypt, sites=sites or [], **kwargs
        )
        self.csv_exporter = self.csv_exporter_cls(
            model_name=self.model, sort_by=sort_by, export_folder=export_folder, **kwargs
        )

    def to_csv(self):
        dataframe = self.df_maker.dataframe
        return self.csv_exporter.to_csv(dataframe=dataframe)

    def to_stata(self):
        dataframe = self.df_maker.dataframe
        return self.csv_exporter.to_stata(dataframe=dataframe)
