from __future__ import annotations

import sys
from pathlib import Path

from django.core.management import CommandError, color_style
from django.core.management.base import BaseCommand

from edc_export.constants import CSV, STATA_14
from edc_export.models_to_file import ModelsToFile
from edc_export.utils import (
    get_default_models_for_export,
    get_export_user,
    get_model_names_for_export,
    get_site_ids_for_export,
    validate_user_perms_or_raise,
)
from edc_sites.site import sites as site_sites

ALL_COUNTRIES = "all"

style = color_style()


class Command(BaseCommand):
    def __init__(self, **kwargs):
        self._countries: list[str] = []
        self.options = {}
        self.decrypt: bool | None = None
        self.site_ids: list[int] = []
        self.exclude_historical: bool | None = None
        super().__init__(**kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            "-a",
            "--app",
            dest="app_labels",
            default="",
            help="app label. Separate by comma if more than one.",
        )

        parser.add_argument(
            "-m",
            "--model",
            dest="model_names",
            default="",
            help="model name in label_lower format. Separate by comma if more than one.",
        )

        parser.add_argument(
            "--trial-prefix",
            dest="trial_prefix",
            default="",
            help="if specified, exports default models for a clinicedc trial",
        )

        parser.add_argument(
            "--skip_model",
            dest="skip_model_names",
            default="",
            help="models to skip in label_lower format. Separate by comma if more than one.",
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
            choices=["csv", "stata"],
            help="export format (csv, stata)",
        )

        parser.add_argument(
            "--stata-dta-version",
            dest="stata_dta_version",
            default=None,
            choices=["118", "119"],
            help="STATA DTA file format version",
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

        parser.add_argument(
            "--use-simple-filename",
            action="store_true",
            dest="use_simple_filename",
            default=False,
            help="do not use app_label or datestamp in filename",
        )

        parser.add_argument(
            "--country",
            dest="countries",
            default="",
            help="only export data for country. Separate by comma if more than one. ",
        )

        parser.add_argument(
            "--site",
            dest="site_ids",
            default="",
            help="only export data for site id. Separate by comma if more than one.",
        )

    def handle(self, *args, **options):  # noqa: ARG002
        user = get_export_user()
        validate_user_perms_or_raise(user, options["decrypt"])

        self.options = options
        self.decrypt = self.options["decrypt"]
        export_format = (
            CSV
            if self.options["format"] == "csv"
            else int(self.options["stata_dta_version"] or STATA_14)
        )

        if not self.options["path"] or not Path(self.options["path"]).expanduser().exists():
            raise CommandError(f"Path does not exist. Got `{self.options['path']}`")
        export_path = Path(self.options["path"]).expanduser().resolve()

        use_simple_filename = self.options["use_simple_filename"]

        sys.stdout.write("Export models.\n")
        sys.stdout.write(f"* export base path: {export_path}\n")

        if self.options["trial_prefix"]:
            model_names = get_default_models_for_export(self.options["trial_prefix"])
        else:
            app_labels = []
            if self.options["app_labels"]:
                app_labels = self.options["app_labels"].split(",")
                sys.stdout.write(
                    f"* preparing to export models from apps: {', '.join(app_labels)}\n"
                )
            model_names = []
            if self.options["model_names"]:
                model_names = self.options["model_names"].split(",")
                sys.stdout.write(f"* preparing to export models: {', '.join(model_names)}\n")
            if not app_labels and not model_names:
                raise CommandError(
                    "Nothing to do. No models to export. "
                    "Specify `app_labels` or `model_names`."
                )
            model_names = get_model_names_for_export(
                app_labels=app_labels,
                model_names=model_names,
            )

        if self.options["skip_model_names"]:
            skip_model_names = self.options["skip_model_names"].split(",")
            sys.stdout.write(f"* skipping models: {', '.join(skip_model_names)}\n")
            model_names = [m for m in model_names if m not in skip_model_names]

        if not self.options["include_historical"]:
            model_names = [m for m in model_names if "historical" not in m]

        # build list of site ids
        site_ids = self.options["site_ids"] or []
        if site_ids:
            site_ids = [int(x) for x in self.options["site_ids"].split(",")]
        site_ids = get_site_ids_for_export(site_ids=site_ids, countries=self.countries)

        # does user have perms to export these sites?
        for site_id in site_ids:
            site_sites.site_in_profile_or_raise(user, site_id)
        sys.stdout.write(
            f"* including data from sites: {', '.join([str(x) for x in site_ids])}\n\n"
        )

        if not model_names:
            raise CommandError("Nothing to do. No models to export.")

        # export
        models_to_file = ModelsToFile(
            user=user,
            models=model_names,
            site_ids=site_ids,
            decrypt=self.decrypt,
            archive_to_single_file=True,
            export_format=export_format,
            use_simple_filename=use_simple_filename,
            export_folder=export_path,
        )
        sys.stdout.write(
            style.SUCCESS(f"\nDone.\nExported to {models_to_file.archive_filename}\n")
        )

    @property
    def countries(self):
        if not self._countries:
            if not self.options["countries"] or self.options["countries"] == ALL_COUNTRIES:
                self._countries = site_sites.countries
            else:
                self._countries = self.options["countries"].lower().split(",")
                for country in self._countries:
                    if country not in site_sites.countries:
                        raise CommandError(f"Invalid country. Got {country}.")
        return self._countries
