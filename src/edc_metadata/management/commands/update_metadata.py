from django.core.management.base import BaseCommand
from django.core.management.color import color_style

from edc_metadata.metadata_refresher import MetadataRefresher

style = color_style()


class Command(BaseCommand):

    help = "Update references, metadata and re-run metadatarules"

    def handle(self, *args, **options):
        metadata_refresher = MetadataRefresher(verbose=True)
        metadata_refresher.run()
