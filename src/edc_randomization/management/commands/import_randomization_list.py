import os

from django.apps import apps as django_apps
from django.core.management.base import BaseCommand, CommandError

from ...randomization_list_importer import RandomizationListImportError
from ...randomization_list_importer import RandomizationListImporter


class Command(BaseCommand):

    help = "Import randomization list"

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            dest="path",
            default=None,
            help=(
                "full path to CSV file. Default: app_config." "randomization_list_path"
            ),
        )

        parser.add_argument(
            "--force-add",
            dest="add",
            default="NO",
            help=("overwrite existing data. CANNOT BE UNDONE!!"),
        )

    def handle(self, *args, **options):
        #         app_config = django_apps.get_app_config("edc_randomization")
        #         path = options["path"] or app_config.randomization_list_path
        #         if not os.path.exists(path or ""):
        #             raise CommandError(f"Invalid path. Got {path}")
        add = options["add"] if options["add"] == "YES" else None
        try:
            RandomizationListImporter(add=add)
        except (RandomizationListImportError, FileNotFoundError) as e:
            raise CommandError(e)
