import sys

from django.core.management.base import BaseCommand
from django.db.models import QuerySet

from edc_metadata.models import CrfMetadata, RequisitionMetadata


class Command(BaseCommand):
    help = (
        "Delete CrfMetadata and RequisitionMetadata records with negative "
        "visit_code_sequence values. These are corrupt records created by a bug in "
        "reset_visit_code_sequence_or_pass() where metadata_create() was called "
        "while visit_code_sequence was temporarily set to a negative value during "
        "renumbering. After running this command, run update_metadata to regenerate "
        "correct metadata for affected subjects."
    )

    def handle(self, *args, **options):  # noqa: ARG002
        crf_qs: QuerySet = CrfMetadata.objects.filter(visit_code_sequence__lt=0)
        req_qs: QuerySet = RequisitionMetadata.objects.filter(visit_code_sequence__lt=0)

        crf_count = crf_qs.count()
        req_count = req_qs.count()

        if crf_count == 0 and req_count == 0:
            sys.stdout.write("No corrupt metadata records found. Nothing to do.\n")
            return

        sys.stdout.write(
            f"Found {crf_count} CrfMetadata and {req_count} RequisitionMetadata "
            "records with negative visit_code_sequence.\n"
        )

        crf_qs.delete()
        sys.stdout.write(f"Deleted {crf_count} CrfMetadata records.\n")

        req_qs.delete()
        sys.stdout.write(f"Deleted {req_count} RequisitionMetadata records.\n")

        sys.stdout.write(
            "Done. Run `update_metadata` to regenerate correct metadata for "
            "affected subjects.\n"
        )
