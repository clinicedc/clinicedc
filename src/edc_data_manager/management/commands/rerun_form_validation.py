from django.core.management.base import BaseCommand, CommandError

from edc_data_manager.form_validation_runners import rerun_form_validation


class Command(BaseCommand):
    help = "Rerun form validation"

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

    def handle(self, *args, **options):
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
        rerun_form_validation(app_labels, model_names)
