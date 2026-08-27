"""Backfill SourceDocument from the folder of original result PDFs.

Results imported before source documents were archived carry only
`source_file`. This links them to an archived copy of the PDF, so the
result-search page can offer the original alongside the parsed values.

Re-importing a folder does not repair these rows: `save_to_model` skips
results already in the table. This command is how they get linked.

Usage::
    manage.py backfill_source_documents /path/to/pdf_folder --laboratory "MNH"
    manage.py backfill_source_documents /path/to/pdf_folder \
        --laboratory "MNH" --dry-run

"""

from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from edc_lab_results_import.models import Result
from edc_lab_results_import.source_documents import archive_source_document, sha256_of


class Command(BaseCommand):
    help = "Backfill SourceDocument from a folder of original result PDFs."

    def add_arguments(self, parser) -> None:
        parser.add_argument("folder", type=str)
        parser.add_argument("--laboratory", dest="laboratory", default=None)
        parser.add_argument("--dry-run", action="store_true", dest="dry_run", default=False)

    def handle(self, *args, **options) -> None:  # noqa: ARG002
        laboratory = options.get("laboratory")
        if not laboratory:
            raise CommandError("--laboratory is required.")
        folder = Path(options["folder"]).expanduser()
        if not folder.is_dir():
            raise CommandError(f"Not a folder. Got {folder}.")
        dry_run = options["dry_run"]

        qs = Result.objects.filter(
            laboratory=laboratory, source_document__isnull=True
        ).exclude(source_file="")
        filenames = sorted(qs.values_list("source_file", flat=True).distinct())

        self.stdout.write(f"{len(filenames)} distinct source_file values to link.")

        linked = missing = deduped = 0
        for filename in filenames:
            path = folder / filename
            if not path.is_file():
                self.stderr.write(f"MISSING  {filename}")
                missing += 1
                continue

            if dry_run:
                self.stdout.write(f"WOULD LINK  {filename}  {sha256_of(path)[:12]}")
                linked += 1
                continue

            with transaction.atomic():
                obj, created = archive_source_document(path, laboratory)
                deduped += not created
                count = Result.objects.filter(
                    laboratory=laboratory,
                    source_file=filename,
                    source_document__isnull=True,
                ).update(source_document=obj)
                linked += 1
                self.stdout.write(f"{filename}  ->  {count} rows")

        self.stdout.write(
            self.style.SUCCESS(f"Done. linked={linked} deduped={deduped} missing={missing}")
        )
