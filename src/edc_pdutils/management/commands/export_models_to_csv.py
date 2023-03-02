import os.path

from django.core.management import CommandError
from django.core.management.base import BaseCommand

from edc_pdutils.df_exporters.csv_exporter import CsvExporter
from edc_pdutils.model_to_dataframe import ModelToDataframe
from edc_pdutils.utils import get_model_names


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-a",
            "--app",
            dest="app_label",
            default=False,
            help="app label",
        )

        parser.add_argument(
            "-p",
            "--path",
            dest="path",
            default=False,
            help="export path",
        )

        parser.add_argument(
            "-f",
            "--format",
            dest="format",
            default="csv",
            help="export format (csv, stata)",
        )

    def handle(self, *args, **options):
        date_format = "%Y-%m-%d"
        sep = "|"
        export_format = options["format"]
        app_label = options["app_label"]
        csv_path = options["path"]
        if not csv_path or not os.path.exists(csv_path):
            raise CommandError(f"Path does not exist. Got `{csv_path}`")
        model_names = get_model_names(app_label=app_label)
        if not app_label or not model_names:
            raise CommandError(f"Nothing to do. No models found in app `{app_label}`")
        for model_name in model_names:
            if "historical" not in model_name:
                m = ModelToDataframe(model=model_name, drop_sys_columns=False)
                exporter = CsvExporter(
                    data_label=model_name,
                    date_format=date_format,
                    delimiter=sep,
                    export_folder=csv_path,
                )
                if not export_format or export_format == "csv":
                    exporter.to_csv(dataframe=m.dataframe)
                elif export_format == "stata":
                    # remove timezone info
                    print(f" * {model_name}")
                    exporter.to_stata(dataframe=m.dataframe)
