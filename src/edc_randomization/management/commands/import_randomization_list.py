from django.core.management.base import BaseCommand, CommandError

from edc_randomization.randomization_list_importer import (
    RandomizationListAlreadyImported,
    RandomizationListImporter,
    RandomizationListImportError,
)
from edc_randomization.site_randomizers import site_randomizers


class Command(BaseCommand):
    help = "Import randomization list"

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            dest="path",
            default=None,
            help="full path to CSV file. Default: app_config.randomization_list_path",
        )

        parser.add_argument(
            "--name", dest="name", default="default", help="name of randomizer"
        )

        parser.add_argument(
            "--force-add",
            dest="add",
            default="NO",
            help="overwrite existing data. CANNOT BE UNDONE!!",
        )

        parser.add_argument(
            "--dryrun",
            dest="dryrun",
            default="NO",
            help="Dry run. No changes will be made",
        )

        parser.add_argument("--user", dest="user", default=None, help="user")

        parser.add_argument("--revision", dest="revision", default=None, help="revision")

    def handle(self, *args, **options):
        """Note: You may not need to do this.

        `import_list()` is usually called when the `randomizer` class
        is first instantiated.
        """
        add = True if options["add"] and options["add"].lower() == "yes" else False
        dryrun = True if options["dryrun"] and options["dryrun"].lower() == "yes" else False
        name = options["name"]
        username = options["user"]
        revision = options["revision"]
        randomizer_cls = site_randomizers.get(name)
        importer = RandomizationListImporter(
            randomizer_cls=randomizer_cls,
            add=add,
            dryrun=dryrun,
            username=username,
            revision=revision,
        )
        try:
            importer.import_list()
        except (
            RandomizationListImportError,
            RandomizationListAlreadyImported,
            FileNotFoundError,
        ) as e:
            raise CommandError(e)
