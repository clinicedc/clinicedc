import sys

from django.core.management.base import BaseCommand

from ...model_exporter import ModelExporter


class Command(BaseCommand):

    help = "Export model objects history for a given app_label.modelname."

    def add_arguments(self, parser):

        parser.add_argument(
            "--models",
            dest="models",
            nargs="*",
            default=None,
            help=("run for a select list of models (label_lower syntax)"),
        )

    def handle(self, *args, **options):
        models = options.get("models")
        for model in models:
            sys.stdout.write(f" ( ) {model} ...\r")
            model_exporter = ModelExporter(model=model)
            path = model_exporter.export()
            sys.stdout.write(f" (*) {model}      \n")
            sys.stdout.write(f"     file: '{path}'\n")
