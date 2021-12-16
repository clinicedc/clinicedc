import sys

from django.core.management.base import BaseCommand
from django.core.management.color import color_style
from edc_visit_schedule import site_visit_schedules

from edc_metadata.metadata_refresher import MetadataRefresher

style = color_style()


class Command(BaseCommand):

    help = "Update references, metadata and re-run metadatarules"

    def add_arguments(self, parser):
        parser.add_argument(
            "--all_metadata_only",
            dest="all_metadata_only",
            default="NO",
            help="YES/NO: Update metadata for all models only",
        )

    def handle(self, *args, **options):
        all_metadata_only = True if options.get("all_metadata_only", "") == "YES" else False
        metadata_refresher = MetadataRefresher(verbose=True)
        if all_metadata_only:
            sys.stdout.write("Updating metadata for all post consent models ...     \n")
            sys.stdout.write("  Note: References will not be updated;\n")
            sys.stdout.write("        Metadata rules will not be run.\n\n")
            metadata_refresher.create_or_update_metadata_for_all(
                site_visit_schedules.all_post_consent_models
            )
        else:
            metadata_refresher.run()
