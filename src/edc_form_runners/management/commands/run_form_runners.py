from django.core.management.base import BaseCommand, CommandError

from edc_form_runners.exceptions import FormRunnerError
from edc_form_runners.run_form_runners import run_form_runners


class Command(BaseCommand):
    help = "Run form runners"

    def add_arguments(self, parser):
        parser.add_argument(
            "-a",
            "--app",
            dest="app_labels",
            default="",
            help="if more than one separate by comma",
        )

        parser.add_argument(
            "-m",
            "--model",
            dest="model_names",
            default="",
            help="model name in label_lower format, if more than one separate by comma",
        )

        parser.add_argument(
            "--debug",
            dest="debug",
            action="store_true",
            default=False,
            help="debug mode",
        )

    def handle(self, *args, **options):
        debug = options["debug"]
        app_labels = options["app_labels"] or []
        if app_labels:
            app_labels = options["app_labels"].split(",")
        model_names = options["model_names"] or []
        if model_names:
            model_names = options["model_names"].split(",")
        if app_labels and model_names:
            raise CommandError(
                "Either provide the `app label` or a `model name` but not both. "
                f"Got {app_labels} and {model_names}."
            )
        try:
            run_form_runners(app_labels, model_names)
        except FormRunnerError as e:
            if debug:
                raise
            raise CommandError(e)
