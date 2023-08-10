from __future__ import annotations

import getpass
import os.path
import sys

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import CommandError, color_style
from django.core.management.base import BaseCommand
from edc_sites.get_countries import get_countries
from edc_sites.get_sites_by_country import get_sites_by_country

from edc_pdutils.df_exporters import Exporter
from edc_pdutils.model_to_dataframe import ModelToDataframe
from edc_pdutils.utils import get_model_names

ALL_COUNTRIES = "all"

style = color_style()


class Command(BaseCommand):
    def __init__(self, **kwargs):
        self.decrypt: bool | None = None
        self.sites: list[int] = []
        self.exclude_historical: bool | None = None
        super().__init__(**kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            "-a",
            "--app",
            dest="app_labels",
            default="",
            help="app label, , if more than one separate by comma",
        )

        parser.add_argument(
            "-m",
            "--model",
            dest="model_names",
            default="",
            help="model name in label_lower format, if more than one separate by comma",
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
                "only export data for country, if more than one separate by "
                f"comma. Use `{ALL_COUNTRIES}` to export all countries."
            ),
        )

        parser.add_argument(
            "--site",
            dest="sites",
            default="",
            help="only export data for site, if more than one separate by comma",
        )

    def handle(self, *args, **options):
        self.validate_user_perms_or_raise()

        date_format = "%Y-%m-%d %H:%M:%S"
        sep = "|"
        export_format = options["format"]
        export_path = options["path"]
        if not export_path or not os.path.exists(export_path):
            raise CommandError(f"Path does not exist. Got `{export_path}`")
        use_simple_filename = options["use_simple_filename"]
        self.exclude_historical = not options["include_historical"]
        self.decrypt = options["decrypt"]

        # TODO: inspect username that you are preparing data for
        sites = options["sites"] or []
        if sites:
            sites = options["sites"].split(",")

        countries = options["countries"] or []
        if not countries:
            raise CommandError("Expected country.")
        else:
            all_countries = get_countries()
            if countries == ALL_COUNTRIES:
                countries = all_countries
            else:
                countries = options["countries"].lower().split(",")
                for country in countries:
                    if country not in all_countries:
                        raise CommandError(f"Invalid country. Got {country}.")

        self.sites = self.get_sites(sites=sites, countries=countries)

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
        models = self.get_models(app_labels=app_labels, model_names=model_names)
        if not models:
            raise CommandError("Nothing to do. No models to export.")

        for app_label, model_names in models.items():
            for model_name in model_names:
                try:
                    m = ModelToDataframe(
                        model=model_name,
                        drop_sys_columns=False,
                        decrypt=self.decrypt,
                        sites=sites,
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
                        exporter.to_stata(dataframe=m.dataframe)
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

    def get_models(
        self, app_labels: list[str] | None, model_names: list[str] | None
    ) -> dict[str, list[str]]:
        models = {}
        if model_names:
            for model_name in model_names:
                app_label, model_name = model_name.split(".")
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
                            app_label=app_label, exclude_historical=self.exclude_historical
                        )
                    }
                )
        return models

    @staticmethod
    def get_sites(
        sites: list[int] | list[str] | None,
        countries: list[str] | None,
    ) -> list[int]:
        if countries and sites:
            raise CommandError("Invalid. Specify `sites` or `countries`, not both.")
        for site in sites or []:
            try:
                obj = Site.objects.get(id=int(site))
            except ObjectDoesNotExist:
                raise CommandError(f"Invalid site. Got `{site}`.")
            else:
                sites.append(obj.id)
        for country in countries or []:
            for single_site in get_sites_by_country(country):
                sites.append(single_site.site_id)
        return sites
