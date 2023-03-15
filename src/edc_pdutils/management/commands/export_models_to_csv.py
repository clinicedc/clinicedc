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

        parser.add_argument(
            "--include-historical",
            action="store_true",
            dest="include_historical",
            default=False,
            help="export historical tables",
        )

        parser.add_argument(
            "--decrypt",
            action="store_true",
            dest="decrypt",
            default=False,
            help="decrypt",
        )

    def handle(self, *args, **options):
        date_format = "%Y-%m-%d %H:%M:%S"
        sep = "|"
        export_format = options["format"]
        app_label = options["app_label"]
        csv_path = options["path"]
        decrypt = options["decrypt"]
        include_historical = options["include_historical"]
        if not csv_path or not os.path.exists(csv_path):
            raise CommandError(f"Path does not exist. Got `{csv_path}`")
        model_names = get_model_names(app_label=app_label)
        if not app_label or not model_names:
            raise CommandError(f"Nothing to do. No models found in app `{app_label}`")
        if not include_historical:
            model_names = [m for m in model_names if "historical" not in m]
        for model_name in model_names:
            m = ModelToDataframe(model=model_name, drop_sys_columns=False, decrypt=decrypt)
            exporter = CsvExporter(
                model_name=model_name,
                date_format=date_format,
                delimiter=sep,
                export_folder=csv_path,
            )
            if not export_format or export_format == "csv":
                exporter.to_csv(dataframe=m.dataframe)
            elif export_format == "stata":
                exporter.to_stata(dataframe=m.dataframe)
            print(f" * {model_name}")
