from __future__ import annotations

import getpass
import os.path
import sys

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import CommandError, color_style
from django.core.management.base import BaseCommand

from edc_model_to_dataframe.model_to_dataframe import ModelToDataframe
from edc_pdutils.df_exporters import Exporter
from edc_pdutils.utils import get_model_names
from edc_sites.site import sites

ALL_COUNTRIES = "all"

style = color_style()


class Command(BaseCommand):
    def __init__(self, **kwargs):
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
            help=(
                "only export data for country. Separate by comma if more than one. "
                f"Use `{ALL_COUNTRIES}` to export all countries."
            ),
        )

        parser.add_argument(
            "--site",
            dest="site_ids",
            default="",
            help="only export data for site id. Separate by comma if more than one.",
        )

    def handle(self, *args, **options):
        self.validate_user_perms_or_raise()

        date_format = "%Y-%m-%d %H:%M:%S"
        sep = "|"
        export_format = options["format"]
        export_path = options["path"]
        stata_dta_version = options["stata_dta_version"]
        if not export_path or not os.path.exists(export_path):
            raise CommandError(f"Path does not exist. Got `{export_path}`")
        use_simple_filename = options["use_simple_filename"]
        self.exclude_historical = not options["include_historical"]
        self.decrypt = options["decrypt"]

        # TODO: inspect username that you are preparing data for
        site_ids = options["site_ids"] or []
        if site_ids:
            site_ids = options["site_ids"].split(",")
        countries = self.get_countries(options)
        self.site_ids = self.get_site_ids(site_ids=site_ids, countries=countries)
        app_labels = options["app_labels"] or []
        if app_labels:
            app_labels = options["app_labels"].split(",")
        model_names = options["model_names"] or []
        if model_names:
            model_names = options["model_names"].split(",")
        skip_model_names = []
        if options["skip_model_names"]:
            skip_model_names = options["skip_model_names"].split(",")
        if app_labels and model_names:
            raise CommandError(
                "Either provide the `app label` or a `model name` but not both. "
                f"Got {app_labels} and {model_names}."
            )
        models = self.get_models(app_labels=app_labels, model_names=model_names)
        if not models:
            raise CommandError("Nothing to do. No models to export.")
        self.export(
            models,
            skip_model_names,
            date_format,
            sep,
            export_path,
            use_simple_filename,
            export_format,
            stata_dta_version,
        )

    def export(
        self,
        models,
        skip_model_names,
        date_format,
        sep,
        export_path,
        use_simple_filename,
        export_format,
        stata_dta_version,
    ):
        for app_label, model_names in models.items():
            for model_name in model_names:
                if model_name in skip_model_names:
                    continue
                try:
                    m = ModelToDataframe(
                        model=model_name,
                        drop_sys_columns=False,
                        decrypt=self.decrypt,
                        sites=self.site_ids,
                    )
                except LookupError as e:
                    sys.stdout.write(style.ERROR(f"     LookupError: {e}\n"))
                else:
                    exporter = Exporter(
                        model_name=model_name,
                        date_format=date_format,
                        delimiter=sep,
                        export_folder=export_path,
                        app_label=app_label,
                        use_simple_filename=use_simple_filename,
                    )
                    if not export_format or export_format == "csv":
                        exporter.to_csv(dataframe=m.dataframe)
                    elif export_format == "stata":
                        exporter.to_stata(dataframe=m.dataframe, dta_version=stata_dta_version)
                    print(f" * {model_name}")

    def validate_user_perms_or_raise(self) -> None:
        username = input("Username:")
        passwd = getpass.getpass("Password for " + username + ":")
        try:
            user = User.objects.get(username=username, is_superuser=False, is_active=True)
        except ObjectDoesNotExist:
            raise CommandError("Invalid username or password.")
        if not user.check_password(passwd):
            raise CommandError("Invalid username or password.")
        if not user.groups.filter(name="EXPORT").exists():
            raise CommandError("You are not authorized to export data.")
        if self.decrypt and not user.groups.filter(name="EXPORT_PII").exists():
            raise CommandError("You are not authorized to export sensitive data.")

    @staticmethod
    def get_countries(options):
        countries = options["countries"] or []
        if not countries:
            raise CommandError("Expected country.")
        if countries == ALL_COUNTRIES:
            countries = sites.countries
        else:
            countries = options["countries"].lower().split(",")
            for country in countries:
                if country not in sites.countries:
                    raise CommandError(f"Invalid country. Got {country}.")
        return countries

    def get_models(
        self, app_labels: list[str] | None, model_names: list[str] | None
    ) -> dict[str, list[str]]:
        models = {}
        if model_names:
            for model_name in model_names:
                app_label, _ = model_name.split(".")
                if self.exclude_historical and model_name.startswith("historical"):
                    continue
                try:
                    models[app_label].append(model_name)
                except KeyError:
                    models[app_label] = [model_name]
        elif app_labels:
            for app_label in app_labels:
                models.update(
                    {
                        app_label: get_model_names(
                            app_label=app_label,
                            exclude_historical=self.exclude_historical,
                        )
                    }
                )
        return models

    @staticmethod
    def get_site_ids(
        site_ids: list[int] | list[str] | None,
        countries: list[str] | None,
    ) -> list[int]:
        if countries and site_ids:
            raise CommandError("Invalid. Specify `site_ids` or `countries`, not both.")
        for site_id in site_ids or []:
            try:
                obj = Site.objects.get(id=int(site_id))
            except ObjectDoesNotExist:
                raise CommandError(f"Invalid site_id. Got `{site_id}`.")
            else:
                site_ids.append(obj.id)
        for country in countries or []:
            site_ids.extend(list(sites.get_by_country(country)))
        return site_ids
