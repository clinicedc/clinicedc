import sys
from warnings import warn

from django.core.management import CommandError
from django.core.management.base import BaseCommand
from django.core.management.color import color_style
from edc_reference.models import Reference

from edc_metadata.metadata_refresher import MetadataRefresher
from edc_metadata.models import CrfMetadata, RequisitionMetadata

style = color_style()


class Command(BaseCommand):
    help = "Update references, metadata and re-run metadatarules"

    def add_arguments(self, parser):
        parser.add_argument(
            "--update_metadata_only",
            dest="update_metadata_only",
            default=False,
            action="store_true",
            help="Update metadata only, skip references (NOT RECOMMENDED)",
        )
        parser.add_argument(
            "--update_references_only",
            dest="update_references_only",
            default=False,
            action="store_true",
            help="Update references only, skip medata. (NOT RECOMMENDED)",
        )

        parser.add_argument(
            "--delete_metadata",
            dest="delete_metadata",
            default=False,
            action="store_true",
            help="delete existing metadata first",
        )

        parser.add_argument(
            "--delete_references",
            dest="delete_references",
            default=False,
            action="store_true",
            help="delete existing references first",
        )

    def handle(self, *args, **options) -> None:
        update_metadata_only = options.get("update_metadata_only")
        update_references_only = options.get("update_references_only")
        delete_metadata = options.get("delete_metadata")
        delete_references = options.get("delete_references")
        if update_metadata_only and update_references_only:
            raise CommandError(
                "Invalid options. Use `update_metadata_only` or `update_references_only` "
                "but not both."
            )
        elif update_metadata_only or update_references_only:
            warn(
                "Option not recommended. Updating metadata and references "
                "separately may lead to unexpected results."
            )
        metadata_refresher = MetadataRefresher(verbose=True)
        if delete_metadata:
            sys.stdout.write("Deleting all CrfMetadata...     \r")
            CrfMetadata.objects.all().delete()
            sys.stdout.write("Deleting all CrfMetadata...done.                    \n")
            sys.stdout.write("Deleting all RequisitionMetadata...     \r")
            RequisitionMetadata.objects.all().delete()
            sys.stdout.write("Deleting all RequisitionMetadata...done.            \n")
        if delete_references:
            sys.stdout.write("Deleting all References...     \r")
            Reference.objects.all().delete()
            sys.stdout.write("Deleting all References...done.                    \n")
        if update_metadata_only:
            sys.stdout.write("Updating metadata for all post consent models ...     \n")
            sys.stdout.write("  Note: References will not be updated;\n")
            sys.stdout.write("        Metadata rules will not be run.\n\n")
            metadata_refresher.create_or_update_metadata_for_all()
        elif update_references_only:
            sys.stdout.write("Updating references for all source models ...     \n")
            sys.stdout.write("  Note: Metadata will not be updated.\n\n")
            metadata_refresher.create_or_update_references_for_all()
        else:
            metadata_refresher.run()
