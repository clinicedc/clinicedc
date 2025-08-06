import sys

from django.core.management.base import BaseCommand
from django.core.management.color import color_style

from edc_metadata.metadata_refresher import MetadataRefresher
from edc_metadata.models import CrfMetadata, RequisitionMetadata

style = color_style()


class Command(BaseCommand):
    help = "Update metadata and re-run metadatarules"

    def handle(self, *args, **options) -> None:
        metadata_refresher = MetadataRefresher(verbose=True)
        sys.stdout.write("Deleting all CrfMetadata...     \r")
        CrfMetadata.objects.all().delete()
        sys.stdout.write("Deleting all CrfMetadata...done.                    \n")
        sys.stdout.write("Deleting all RequisitionMetadata...     \r")
        RequisitionMetadata.objects.all().delete()
        sys.stdout.write("Deleting all RequisitionMetadata...done.            \n")
        metadata_refresher.run()
