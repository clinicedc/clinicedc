from __future__ import annotations

import grp
import os
import pwd
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


def _split_csv(value: str | None) -> list[str]:
    """Split a comma-separated CLI value, stripping whitespace and
    dropping empty tokens. Handles trailing commas and stray spaces.
    """
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _validate_export_path_or_raise(path: Path, decrypt: bool) -> list[str]:
    """Validate the export directory. Returns a list of warnings
    (non-fatal). Raises CommandError on any hard-error condition.

    Hard errors:
      - path does not exist, is not a directory, or is not writable
      - with decrypt, directory is world-readable (o+r)

    Warnings:
      - with decrypt, directory is group-readable and the group is
        not "private" (has members besides the owner)
    """
    if not path.exists():
        raise CommandError(f"Path does not exist. Got `{path}`.")
    if not path.is_dir():
        raise CommandError(f"Path is not a directory. Got `{path}`.")
    if not os.access(path, os.W_OK):
        raise CommandError(f"Path is not writable. Got `{path}`.")

    warnings: list[str] = []
    if decrypt:
        st = path.stat()
        mode = st.st_mode
        if mode & 0o004:
            raise CommandError(
                "Refusing to write decrypted data to a world-readable "
                f"directory. Got `{path}` (mode {oct(mode & 0o777)}). "
                "Remove world-read (chmod o-r) and retry."
            )
        if mode & 0o040:
            # group-readable; warn only if group is non-private
            try:
                group_info = grp.getgrgid(st.st_gid)
                owner_name = pwd.getpwuid(st.st_uid).pw_name
                primary_members = {
                    p.pw_name for p in pwd.getpwall() if p.pw_gid == st.st_gid
                }
                all_members = set(group_info.gr_mem) | primary_members
                if not all_members <= {owner_name}:
                    warnings.append(
                        f"Export directory `{path}` is group-readable by "
                        f"group `{group_info.gr_name}` which has members "
                        f"beyond the owner `{owner_name}`. Decrypted data "
                        "will be readable by those users."
                    )
            except KeyError:
                # unknown uid/gid — can't verify; warn conservatively
                warnings.append(
                    f"Export directory `{path}` is group-readable and "
                    "group membership could not be verified."
                )
    return warnings


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

    def handle(self, *args, **options):  # noqa: ARG002, C901, PLR0912
        user = get_export_user()
        validate_user_perms_or_raise(user, options["decrypt"])

        self.options = options
        self.decrypt = self.options["decrypt"]
        export_format = (
            CSV
            if self.options["format"] == "csv"
            else int(self.options["stata_dta_version"] or STATA_14)
        )

        if not self.options["path"]:
            raise CommandError("Path is required. Use --path to specify the export directory.")
        export_path = Path(self.options["path"]).expanduser().resolve()
        warnings = _validate_export_path_or_raise(export_path, decrypt=bool(self.decrypt))

        use_simple_filename = self.options["use_simple_filename"]

        sys.stdout.write("Export models.\n")
        sys.stdout.write(f"* export base path: {export_path}\n")
        for warning in warnings:
            sys.stderr.write(style.WARNING(f"WARNING: {warning}\n"))

        app_labels = _split_csv(self.options["app_labels"])
        cli_model_names = _split_csv(self.options["model_names"])

        if self.options["trial_prefix"]:
            if app_labels or cli_model_names:
                raise CommandError(
                    "`--trial-prefix` is mutually exclusive with `--app` and `--model`."
                )
            model_names = get_default_models_for_export(self.options["trial_prefix"])
        else:
            if app_labels:
                sys.stdout.write(
                    f"* preparing to export models from apps: {', '.join(app_labels)}\n"
                )
            if cli_model_names:
                sys.stdout.write(
                    f"* preparing to export models: {', '.join(cli_model_names)}\n"
                )
            if not app_labels and not cli_model_names:
                raise CommandError(
                    "Nothing to do. No models to export. "
                    "Specify `app_labels` or `model_names`."
                )
            model_names = get_model_names_for_export(
                app_labels=app_labels,
                model_names=cli_model_names,
            )

        skip_model_names = _split_csv(self.options["skip_model_names"])
        if skip_model_names:
            sys.stdout.write(f"* skipping models: {', '.join(skip_model_names)}\n")
            model_names = [m for m in model_names if m not in skip_model_names]

        if not self.options["include_historical"]:
            model_names = [m for m in model_names if "historical" not in m]

        # build list of site ids
        site_ids_raw = _split_csv(self.options["site_ids"])
        try:
            site_ids = [int(x) for x in site_ids_raw]
        except ValueError as e:
            raise CommandError(
                f"Invalid --site value, must be integers. Got `{self.options['site_ids']}`."
            ) from e
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
            raw = (self.options["countries"] or "").strip().lower()
            if not raw:
                self._countries = []
            elif raw == ALL_COUNTRIES:
                self._countries = list(site_sites.countries)
            else:
                self._countries = [c.lower() for c in _split_csv(raw)]
                for country in self._countries:
                    if country not in site_sites.countries:
                        raise CommandError(f"Invalid country. Got {country}.")
        return self._countries
