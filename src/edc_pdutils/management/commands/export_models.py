import getpass
import os.path

from django.contrib.auth.models import Group, User
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import CommandError
from django.core.management.base import BaseCommand

from edc_pdutils.df_exporters import Exporter
from edc_pdutils.model_to_dataframe import ModelToDataframe
from edc_pdutils.utils import get_model_names


class Command(BaseCommand):
    def __init__(self, **kwargs):
        self.decrypt = None
        super().__init__(**kwargs)

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

        parser.add_argument(
            "--use-simple-filename",
            action="store_true",
            dest="use_simple_filename",
            default=False,
            help="do not use app_label or datestamp in filename",
        )

    def handle(self, *args, **options):
        date_format = "%Y-%m-%d %H:%M:%S"
        sep = "|"
        export_format = options["format"]
        app_label = options["app_label"]
        export_path = options["path"]
        use_simple_filename = options["use_simple_filename"]
        include_historical = options["include_historical"]
        self.decrypt = options["decrypt"]
        # self.validate_user_perms_or_raise()
        if not export_path or not os.path.exists(export_path):
            raise CommandError(f"Path does not exist. Got `{export_path}`")
        model_names = get_model_names(app_label=app_label)
        if not app_label or not model_names:
            raise CommandError(f"Nothing to do. No models found in app `{app_label}`")
        if not include_historical:
            model_names = [m for m in model_names if "historical" not in m]
        for model_name in model_names:
            m = ModelToDataframe(
                model=model_name, drop_sys_columns=False, decrypt=self.decrypt
            )
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
            raise CommandError("You are not authorized to export data. (1)")
        if not user.check_password(passwd):
            raise CommandError("You are not authorized to export data. (2)")
        group = Group.objects.get(name="EXPORT")
        if not user.has_perms([o.codename for o in group.permissions.all()]):
            raise CommandError("You are not authorized to export data. (3)")
        if self.decrypt:
            group = Group.objects.get(name="PII")
            if not user.has_perms([o.codename for o in group.permissions.all()]):
                raise CommandError("You are not authorized to export data. (4)")
