from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING


from django.core.management.color import color_style

from .dataframe_exporter import DataframeExporter

if TYPE_CHECKING:
    from django.db.models import QuerySet
    import pandas as pd

style = color_style()


class ModelExporter:
    def __init__(
        self,
        dataframe: pd.DataFrame,
        *,
        export_folder: Path,
        model: str | None = None,
        queryset: QuerySet | None = None,
        sort_by: list | tuple | str | None = None,
    ):
        self.queryset = queryset
        self.model = model or queryset.model._meta.label_lower
        self.export_folder = export_folder

        self.df_exporter = DataframeExporter(
            model_name=self.model,
            sort_by=sort_by,
            export_folder=export_folder,
        )

    def to_csv(self):
        return self.df_exporter.to_csv(
            dataframe=self.dataframe, export_folder=self.export_folder
        )

    def to_stata(self):
        return self.df_exporter.to_stata(
            dataframe=self.dataframe, export_folder=self.export_folder
        )
