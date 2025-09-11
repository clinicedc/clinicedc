from django.apps import apps as django_apps
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
            "-s",
            "--skip_model",
            dest="skip_model_names",
            default="",
            help="model to skip in label_lower format, if more than one separate by comma",
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

        skip_model_names = options["skip_model_names"] or []
        if skip_model_names:
            skip_model_names = options["skip_model_names"].split(",")

        if app_labels and model_names:
            raise CommandError(
                "Either provide the `app label` or `model name(s)` but not both. "
                f"Got {app_labels} and {model_names}."
            )

        # if app_labels:
        #     for app_config in django_apps.get_app_configs():
        #         if app_config.name in app_labels:
        #             for model_cls in app_config.get_models():
        #                 if not model_cls._meta.label_lower.split(".")[1].startswith(
        #                     "historical"
        #                 ):
        #                     model_names.append(model_cls._meta.label_lower)
        #
        # model_names = [m for m in model_names if m not in skip_model_names]
        model_names = get_model_names(app_labels, model_names, skip_model_names)

        try:
            run_form_runners(model_names=model_names)
        except FormRunnerError as e:
            if debug:
                raise
            raise CommandError(e)


def get_model_names(app_labels, model_names, skip_model_names):
    if app_labels:
        for app_config in django_apps.get_app_configs():
            if app_config.name in app_labels:
                for model_cls in app_config.get_models():
                    if not model_cls._meta.label_lower.split(".")[1].startswith("historical"):
                        model_names.append(model_cls._meta.label_lower)

    return [m for m in model_names if m not in skip_model_names]
