"""Import lab results from a folder of PDF files.

The parser is resolved from the EDC_LAB_RESULTS_PARSERS setting,
keyed by laboratory name.

Usage::

    manage.py import_labs /path/to/pdf_folder --laboratory "MNH"
    manage.py import_labs /path/to/pdf_folder \
        --laboratory "MNH" --dry-run
    manage.py import_labs /path/to/pdf_folder \
        --laboratory "MNH" --output /path/to/output.csv
    manage.py import_labs --pending --laboratory "MNH"
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from edc_lab_results.import_results import (
    LabResultImporter,
    LabResultImportError,
    check_utest_id_conflict,
)
from edc_lab_results.models import UploadedResultFile


def _make_prompt_func(stdout, style):
    """Return a prompt callback wired to the command's stdout/style."""

    def prompt_func(
        investigation: str, guess: str, laboratory: str
    ) -> str:
        stdout.write("")
        stdout.write(style.WARNING(f"  Unknown investigation: {investigation}"))

        while True:
            if guess:
                stdout.write(f"  Best guess: {guess}")
                prompt = (
                    f"  Enter utest_id for '{investigation}' "
                    f"[{guess}] or 'u' for unknown: "
                )
            else:
                stdout.write("  Best guess: (no match)")
                prompt = (
                    f"  Enter utest_id for '{investigation}' "
                    f"or press Enter for unknown: "
                )

            answer = input(prompt).strip().lower()

            if answer == "u" or (not answer and not guess):
                return ""
            utest_id = guess if not answer and guess else answer

            conflict = check_utest_id_conflict(
                utest_id, investigation, laboratory
            )
            if conflict:
                stdout.write(
                    style.ERROR(
                        f"  '{utest_id}' is already mapped to "
                        f"'{conflict}'. Try again."
                    )
                )
                guess = ""
                continue
            return utest_id

    return prompt_func


class Command(BaseCommand):
    help = "Import lab results from a folder of PDF files."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "folder",
            nargs="?",
            type=str,
            default=None,
            help="Path to folder containing lab result PDF files.",
        )
        parser.add_argument(
            "--laboratory",
            dest="laboratory",
            default=None,
            help="Laboratory name (e.g. 'MNH'). Required except for --show-pending.",
        )
        parser.add_argument(
            "--output",
            dest="output",
            default=None,
            help=(
                "Output CSV path. Defaults to lab_results.csv "
                "inside the PDF folder."
            ),
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            default=False,
            help="Parse and report without saving to the database.",
        )
        parser.add_argument(
            "--pending",
            action="store_true",
            dest="pending",
            default=False,
            help="Process all pending uploaded files instead of a folder.",
        )
        parser.add_argument(
            "--show-pending",
            action="store_true",
            dest="show_pending",
            default=False,
            help="List all pending uploaded files and exit.",
        )

    def handle(self, *args, **options) -> None:  # noqa: ARG002
        if options["show_pending"]:
            self._handle_show_pending()
        elif options["pending"]:
            self._handle_pending(options)
        else:
            self._handle_folder(options)

    def _handle_show_pending(self) -> None:
        pending_files = UploadedResultFile.objects.filter(status="pending")
        count = pending_files.count()
        if not count:
            self.stdout.write("No pending files.")
            return
        self.stdout.write(f"{count} pending file(s):\n")
        for upload in pending_files:
            self.stdout.write(
                f"  {upload.original_filename}  "
                f"(stored as {upload.stored_filename}, "
                f"uploaded {upload.uploaded_datetime:%Y-%m-%d %H:%M} "
                f"by {upload.uploaded_by.username})"
            )

    @staticmethod
    def _require_laboratory(options: dict) -> str:
        laboratory = options.get("laboratory")
        if not laboratory:
            raise CommandError("--laboratory is required.")
        return laboratory

    def _handle_folder(self, options: dict) -> None:
        folder_arg = options.get("folder")
        if not folder_arg:
            raise CommandError(
                "A folder path is required unless --pending is used."
            )
        folder = Path(folder_arg).expanduser()
        laboratory = self._require_laboratory(options)
        output_path = (
            Path(options["output"]).expanduser()
            if options["output"]
            else folder / "lab_results.csv"
        )

        prompt_func = _make_prompt_func(self.stdout, self.style)
        importer = LabResultImporter(
            laboratory, prompt_func=prompt_func
        )

        try:
            tz = ZoneInfo(settings.TIME_ZONE)
            self.stdout.write(f"Parsing PDFs from {folder} ...")
            df = importer.parse(folder, tz=tz, output_path=output_path)
        except LabResultImportError as e:
            raise CommandError(str(e)) from e

        if df.empty:
            self.stdout.write(self.style.WARNING("No results extracted."))
            return

        self.stdout.write(f"CSV saved to {output_path}")
        self._import_dataframe(importer, df, laboratory, options)

    def _handle_pending(self, options: dict) -> None:
        pending_files = UploadedResultFile.objects.filter(status="pending")
        count = pending_files.count()
        if not count:
            self.stdout.write("No pending files to process.")
            return

        self.stdout.write(f"Processing {count} pending file(s) ...")
        base_dir = Path(settings.EDC_LAB_RESULTS_UPLOAD_DIR).expanduser()
        pending_dir = base_dir / "pending"
        processed_dir = base_dir / "processed"

        laboratory = self._require_laboratory(options)
        prompt_func = _make_prompt_func(self.stdout, self.style)
        tz = ZoneInfo(settings.TIME_ZONE)

        for upload in pending_files:
            source = pending_dir / upload.stored_filename
            if not source.exists():
                upload.status = "error"
                upload.error_message = f"File not found: {source}"
                upload.save(update_fields=["status", "error_message"])
                self.stdout.write(
                    self.style.ERROR(
                        f"  {upload.original_filename}: file not found"
                    )
                )
                continue

            self.stdout.write(f"  Processing {upload.original_filename} ...")
            importer = LabResultImporter(laboratory, prompt_func=prompt_func)
            try:
                df = importer.parse_files([source], tz=tz)
                if df.empty:
                    upload.status = "imported"
                    upload.imported_datetime = timezone.now()
                    upload.error_message = "No results extracted."
                    upload.save(
                        update_fields=[
                            "status",
                            "imported_datetime",
                            "error_message",
                        ]
                    )
                    self.stdout.write(
                        self.style.WARNING(
                            f"    {upload.original_filename}: "
                            f"no results extracted"
                        )
                    )
                else:
                    self._import_dataframe(
                        importer, df, laboratory, options
                    )
                    upload.status = "imported"
                    upload.imported_datetime = timezone.now()
                    upload.save(
                        update_fields=["status", "imported_datetime"]
                    )
                shutil.move(str(source), str(processed_dir / upload.stored_filename))
            except Exception as e:
                upload.status = "error"
                upload.error_message = str(e)
                upload.save(update_fields=["status", "error_message"])
                self.stdout.write(
                    self.style.ERROR(
                        f"    {upload.original_filename}: {e}"
                    )
                )

        self.stdout.write(self.style.SUCCESS("Pending files processed."))

    def _import_dataframe(
        self,
        importer: LabResultImporter,
        df: object,
        laboratory: str,
        options: dict,
    ) -> None:
        self.stdout.write(
            f"Resolving investigation mappings for "
            f"laboratory '{laboratory}' ..."
        )
        mapping_summary = importer.resolve_mappings(df)
        self.stdout.write(
            f"Mappings: {mapping_summary.mapped} mapped, "
            f"{mapping_summary.unmapped} unknown to EDC."
        )

        if mapping_summary.not_in_reportable:
            self.stdout.write(
                self.style.WARNING(
                    "The following utest_ids are NOT in "
                    "reportable normal data:"
                )
            )
            for inv, uid in mapping_summary.not_in_reportable:
                self.stdout.write(f"  {inv} -> {uid}")

        if options["dry_run"]:
            self.stdout.write(
                self.style.WARNING(
                    f"Dry run: {len(df)} results parsed, not saved."
                )
            )
            return

        save_summary = importer.save_results(
            df, mapping_summary.utest_map
        )

        msg = (
            f"Created {save_summary.created} results from "
            f"{df['source_file'].nunique()} files."
        )
        if save_summary.skipped:
            msg += f" Skipped {save_summary.skipped} duplicates."
        self.stdout.write(self.style.SUCCESS(msg))

        if save_summary.unresolved:
            self.stdout.write(
                self.style.WARNING(
                    f"{save_summary.unresolved} results could not be "
                    f"resolved to a subject_identifier or "
                    f"screening_identifier (flagged as subject_not_found)."
                )
            )

        if save_summary.unrecognized_units:
            self.stdout.write(
                self.style.WARNING(
                    "The following units could not be converted "
                    "(no matching NormalData formula or conversion path):"
                )
            )
            for utest_id, units in sorted(save_summary.unrecognized_units):
                self.stdout.write(f"  {utest_id}: {units}")

        link_summary = importer.link_requisitions()
        self.stdout.write(
            self.style.SUCCESS(
                f"Requisition matching: {link_summary.linked} matched, "
                f"{link_summary.ambiguous} ambiguous (flagged), "
                f"{link_summary.no_match} no match."
            )
        )

        sys.stdout.flush()
