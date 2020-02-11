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

        parser.add_argument(
            "--revision", dest="revision", default=None, help="revision"
        )

    def handle(self, *args, **options):
        add = options["add"] if options["add"] == "YES" else None
        dryrun = options["dryrun"]
        name = options["name"]
        user = options["user"]
        revision = options["revision"]
        try:
            RandomizationListImporter(
                name=name, add=add, dryrun=dryrun, user=user, revision=revision
            )
        except (RandomizationListImportError, FileNotFoundError) as e:
            raise CommandError(e)
