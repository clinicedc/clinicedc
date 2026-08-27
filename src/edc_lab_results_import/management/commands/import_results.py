"""Import lab results from a folder of PDF files.

The parser is resolved from the EDC_LAB_RESULTS_PARSERS setting, and the
utestid/unit mappings are resolved from the EDC_LAB_RESULTS_MAPPING_FILES
setting, both keyed by laboratory name.

Usage::
    manage.py import_results /path/to/pdf_folder --laboratory "MNH"
    manage.py import_results /path/to/pdf_folder \
        --laboratory "MNH" --dry-run

"""

from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from edc_identifier.utils import is_valid_subject_identifier
from edc_lab_results_import.result_importer import ResultImporter


class Command(BaseCommand):
    """Import lab results from a folder of PDF files.

    See also module `download-gmail-pdfs` if fetching PDFs
    from Gmail.
    """

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
            help="Laboratory name (e.g. 'MNH'). Required.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            default=False,
            help="Parse and report without saving to the database.",
        )

        parser.add_argument(
            "--duplicates-json-path",
            action="store_true",
            dest="duplicates_json_path",
            default=None,
            help="Path and filename for existing duplicates JSON mapping.",
        )

    def handle(self, *args, **options) -> None:  # noqa: ARG002
        if not options.get("laboratory"):
            raise CommandError("--laboratory is required.")
        self.import_results(options)

    def import_results(self, options: dict) -> None:
        path = options.get("folder", "")
        if not path:
            raise CommandError("A folder path is required.")
        path = Path(path).expanduser()
        duplicates_json_path = options.get("duplicates_json_path")
        if duplicates_json_path:
            if not Path(duplicates_json_path).expanduser().exists():
                raise CommandError(
                    f"Duplicate mapping does not exist. Got {duplicates_json_path}."
                )
            duplicates_json_path = Path(duplicates_json_path).expanduser()
        laboratory: str = options.get("laboratory", "")
        dry_run = options.get("dry_run")
        importer = ResultImporter(
            laboratory,
            path,
            stdout=self.stdout,
            dry_run=dry_run,
            duplicates_json_path=duplicates_json_path,
            is_valid_identifier_func=is_valid_subject_identifier,
        )
        importer.run(to_model=True, df_to_path=path)
