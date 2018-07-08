from django.core.management.color import color_style

from ..model_to_dataframe import ModelToDataframe
from .csv_exporter import CsvExporter


style = color_style()


class CsvModelExporter:

    df_maker_cls = ModelToDataframe
    csv_exporter_cls = CsvExporter

    def __init__(self, model=None, queryset=None, decrypt=None, sort_by=None,
                 **kwargs):
        self.model = model or queryset.model._meta.label_lower
        self.df_maker = self.df_maker_cls(
            model=model, queryset=queryset, decrypt=decrypt, **kwargs)
        self.csv_exporter = self.csv_exporter_cls(
            data_label=self.model, sort_by=sort_by, **kwargs)

    def to_csv(self):
        return self.csv_exporter.to_csv(self.df_maker.dataframe)
