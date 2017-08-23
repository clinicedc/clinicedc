import os

from django.core.management.color import color_style

from ..model_to_dataframe import ModelToDataframe
from .csv_exporter import CsvExporter


style = color_style()


class CsvModelExporter(CsvExporter):

    dataframe_maker_cls = ModelToDataframe

    def __init__(self, model=None, queryset=None, decrypt=None, **kwargs):
        self.dataframe_maker = self.dataframe_maker_cls(
            model=model, queryset=queryset,
            decrypt=decrypt, **kwargs)
        self.model = self.dataframe_maker.model

    def to_csv(self, include_index=None, exists_ok=None):
        return super().to_csv(
            label=self.model,
            dataframe=self.dataframe_maker.dataframe,
            exists_ok=exists_ok,
            include_index=include_index)
