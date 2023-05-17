import sys
from typing import Optional

from django.core.management.base import BaseCommand
from django.core.management.color import color_style
from edc_protocol.protocol import Protocol

from edc_reportable.site_reportables import site_reportables

style = color_style()


def export_daids_grading(path: Optional[str]):
    sys.stdout.write(style.MIGRATE_HEADING("Exporting reportables to document (.csv) ...\n"))
    collection_name = Protocol().project_name.lower()
    filename1, filename2 = site_reportables.to_csv(collection_name=collection_name, path=path)
    sys.stdout.write(
        style.MIGRATE_HEADING(f"  * Exported to `{filename1}` and `{filename2}`\n")
    )
    sys.stdout.write(style.MIGRATE_HEADING("Done\n"))


class Command(BaseCommand):
    help = "Export export DAIDS grading to document (.csv)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="~/",
            action="store_true",
            dest="path",
            help="Export path/folder",
        )

    def handle(self, *args, **options):
        export_daids_grading(path=options["path"])
