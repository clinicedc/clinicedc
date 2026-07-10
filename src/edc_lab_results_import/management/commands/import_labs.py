"""Import lab results from a folder of PDF files.

The parser is resolved from the EDC_LAB_RESULTS_PARSERS setting,
keyed by laboratory name.

Usage::
    manage.py import_labs /path/to/pdf_folder --laboratory "MNH"
    manage.py import_labs /path/to/pdf_folder \
        --laboratory "MNH" --dry-run

The --mappings JSON file format::

    {
        "Haemoglobin": "hgb",
        "White Cell Count": "wbc",
        "Platelet Count": "platelets",
        "Glucose (Fasting)": ""
    }

"""

from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from edc_lab_results_import.exceptions import ResultImporterError
from edc_lab_results_import.result_importer import ResultImporter


class Command(BaseCommand):
    """Import lab results from a folder of PDF files.

    See also script `download_gmail_pdfs` if fetching PDFs
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
            help="Laboratory name (e.g. 'MNH'). Required except for --show-pending.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            default=False,
            help="Parse and report without saving to the database.",
        )

    def handle(self, *args, **options) -> None:  # noqa: ARG002
        if not options.get("laboratory"):
            raise CommandError("--laboratory is required.")
        self.import_results(options)

    def import_results(self, options: dict) -> None:
        path = options.get("folder", "")
        if not path:
            raise CommandError("A folder path is required unless --pending is used.")
        path = Path(path).expanduser()
        laboratory: str = options.get("laboratory", "")
        dry_run = options.get("dry_run")
        importer = ResultImporter(laboratory, path, stdout=self.stdout, dry_run=dry_run)
        self.stdout.write(f"Parsing PDFs from {path} ...")
        try:
            df = importer.parse_pdfs_to_dataframe()
        except ResultImporterError as e:
            raise CommandError(str(e)) from e

        if df.empty:
            self.stdout.write(self.style.WARNING("No results extracted."))
        else:
            importer.dataframe_to_model(df)
