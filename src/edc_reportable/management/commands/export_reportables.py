import sys
from pathlib import Path

from django.core.management.base import BaseCommand
from django.core.management.color import color_style
from django_pandas.io import read_frame

from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_reportable.models import GradingData, NormalData

style = color_style()


def export_daids_grading(path: str, reference_range_collection_name: str | None = None):
    path = Path(path or "~/").expanduser()
    sys.stdout.write(style.MIGRATE_HEADING("Exporting reportables to document (.csv) ...\n"))
    reference_range_collection_name = (
        reference_range_collection_name or ResearchProtocolConfig().project_name.lower()
    )
    df = read_frame(
        GradingData.objects.filter(
            reference_range_collection__name=reference_range_collection_name
        ),
        verbose=True,
    )
    fname = path / f"{reference_range_collection_name}_grading_data.csv"
    df.to_csv(fname, index=False)
    sys.stdout.write(style.MIGRATE_HEADING(f"  * Exported grading data to `{fname}`\n"))
    df = read_frame(
        NormalData.objects.filter(
            reference_range_collection__name=reference_range_collection_name
        ),
        verbose=True,
    )
    fname = path / f"{reference_range_collection_name}_normal_data.csv"
    df.to_csv(fname, index=False)
    sys.stdout.write(style.MIGRATE_HEADING(f"  * Exported normal data to `{fname}`\n"))
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
