"""Import lab results from a folder of PDF files.

PDFs are read from the upload folder, settings
EDC_LAB_RESULTS_IMPORT_UPLOAD_DIR, unless a folder is given. Each PDF
is archived into the storage folder, settings
EDC_LAB_RESULTS_IMPORT_STORAGE_DIR.

The parser is resolved from the EDC_LAB_RESULTS_PARSERS setting, and the
utestid/unit mappings are resolved from the EDC_LAB_RESULTS_MAPPING_FILES
setting, both keyed by laboratory name.

Usage::
    manage.py import_results --laboratory "MNH"
    manage.py import_results --laboratory "MNH" --dry-run
    manage.py import_results /path/to/pdf_folder --laboratory "MNH"

"""

from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from edc_identifier.utils import is_valid_subject_identifier
from edc_lab_panel.panels import wbc_differential
from edc_lab_results_import.exceptions import (
    EdcLabResultsUploadDirError,
    ResultImporterError,
)
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
            help=(
                "Path to folder containing lab result PDF files. "
                "Defaults to settings.EDC_LAB_RESULTS_IMPORT_UPLOAD_DIR."
            ),
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
            dest="duplicates_json_path",
            default=None,
            help="Path and filename for existing duplicates JSON mapping.",
        )

        parser.add_argument(
            "--df-to-path",
            dest="df_to_path",
            default=None,
            help="Folder to write the parsed dataframes to as parquet. Optional.",
        )

    def handle(self, *args, **options) -> None:  # noqa: ARG002
        if not options.get("laboratory"):
            raise CommandError("--laboratory is required.")
        self.import_results(options)

    def import_results(self, options: dict) -> None:
        path = options.get("folder")
        path = Path(path).expanduser() if path else None
        df_to_path = options.get("df_to_path")
        if df_to_path:
            df_to_path = Path(df_to_path).expanduser()
            if not df_to_path.is_dir():
                raise CommandError(f"Folder does not exist. Got {df_to_path}.")
        duplicates_json_path = options.get("duplicates_json_path")
        if duplicates_json_path:
            if not Path(duplicates_json_path).expanduser().exists():
                raise CommandError(
                    f"Duplicate mapping does not exist. Got {duplicates_json_path}."
                )
            duplicates_json_path = Path(duplicates_json_path).expanduser()
        laboratory: str = options.get("laboratory", "")
        dry_run = options.get("dry_run")
        try:
            importer = ResultImporter(
                laboratory,
                path,
                stdout=self.stdout,
                dry_run=dry_run,
                duplicates_json_path=duplicates_json_path,
                is_valid_identifier_func=is_valid_subject_identifier,
                # the differential analytes are reported under their own
                # panel, which no lab profile registers because they are
                # drawn under FBC. Without it every differential utest id
                # resolves to no panel and the result can never be matched
                # to a requisition
                extra_panels=[wbc_differential],
            )
        except (EdcLabResultsUploadDirError, ResultImporterError) as e:
            raise CommandError(str(e)) from e
        importer.run(to_model=True, df_to_path=df_to_path)
