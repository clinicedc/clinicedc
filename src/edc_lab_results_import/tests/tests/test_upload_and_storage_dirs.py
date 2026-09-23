from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase, override_settings, tag

from edc_lab_results_import.exceptions import (
    EdcLabResultsStorageDirError,
    EdcLabResultsUploadDirError,
    ResultImporterError,
)
from edc_lab_results_import.result_importer.result_importer import ResultImporter
from edc_lab_results_import.system_checks import (
    storage_dir_check,
    upload_and_storage_dirs_check,
    upload_dir_check,
)
from edc_lab_results_import.utils import get_storage_dir, get_upload_dir

MODULE = "edc_lab_results_import.result_importer.result_importer"


def error_ids(errors: list) -> list[str]:
    return [error.id for error in errors]


@tag("lab_results_import")
class TestUploadAndStorageDirs(SimpleTestCase):
    def setUp(self):
        self.storage_dir = tempfile.mkdtemp()
        self.upload_dir = tempfile.mkdtemp()

    def test_getters(self):
        with override_settings(
            EDC_LAB_RESULTS_IMPORT_STORAGE_DIR=self.storage_dir,
            EDC_LAB_RESULTS_IMPORT_UPLOAD_DIR=self.upload_dir,
        ):
            self.assertEqual(get_storage_dir(), Path(self.storage_dir))
            self.assertEqual(get_upload_dir(), Path(self.upload_dir))

    @override_settings(
        EDC_LAB_RESULTS_IMPORT_STORAGE_DIR=None, EDC_LAB_RESULTS_IMPORT_UPLOAD_DIR=None
    )
    def test_getters_raise_if_not_set(self):
        self.assertRaises(EdcLabResultsStorageDirError, get_storage_dir)
        self.assertRaises(EdcLabResultsUploadDirError, get_upload_dir)

    def test_getters_raise_if_folder_does_not_exist(self):
        with override_settings(
            EDC_LAB_RESULTS_IMPORT_STORAGE_DIR=Path(self.storage_dir) / "missing",
            EDC_LAB_RESULTS_IMPORT_UPLOAD_DIR=Path(self.upload_dir) / "missing",
        ):
            self.assertRaises(EdcLabResultsStorageDirError, get_storage_dir)
            self.assertRaises(EdcLabResultsUploadDirError, get_upload_dir)

    def test_checks_pass(self):
        with override_settings(
            EDC_LAB_RESULTS_IMPORT_STORAGE_DIR=self.storage_dir,
            EDC_LAB_RESULTS_IMPORT_UPLOAD_DIR=self.upload_dir,
        ):
            self.assertEqual(storage_dir_check(None), [])
            self.assertEqual(upload_dir_check(None), [])
            self.assertEqual(upload_and_storage_dirs_check(None), [])

    @override_settings(
        EDC_LAB_RESULTS_IMPORT_STORAGE_DIR=None, EDC_LAB_RESULTS_IMPORT_UPLOAD_DIR=None
    )
    def test_checks_not_set(self):
        """Reported, not raised."""
        self.assertEqual(error_ids(storage_dir_check(None)), ["edc_lab_results_import.E004"])
        self.assertEqual(error_ids(upload_dir_check(None)), ["edc_lab_results_import.E006"])
        self.assertEqual(upload_and_storage_dirs_check(None), [])

    def test_checks_folder_does_not_exist(self):
        with override_settings(
            EDC_LAB_RESULTS_IMPORT_STORAGE_DIR=Path(self.storage_dir) / "missing",
            EDC_LAB_RESULTS_IMPORT_UPLOAD_DIR=Path(self.upload_dir) / "missing",
        ):
            self.assertEqual(
                error_ids(storage_dir_check(None)), ["edc_lab_results_import.E005"]
            )
            self.assertEqual(
                error_ids(upload_dir_check(None)), ["edc_lab_results_import.E007"]
            )

    def test_check_upload_dir_is_storage_dir(self):
        with override_settings(
            EDC_LAB_RESULTS_IMPORT_STORAGE_DIR=self.storage_dir,
            EDC_LAB_RESULTS_IMPORT_UPLOAD_DIR=self.storage_dir,
        ):
            self.assertEqual(
                error_ids(upload_and_storage_dirs_check(None)),
                ["edc_lab_results_import.E008"],
            )

    def test_check_upload_dir_inside_storage_dir(self):
        upload_dir = Path(self.storage_dir) / "upload"
        upload_dir.mkdir()
        with override_settings(
            EDC_LAB_RESULTS_IMPORT_STORAGE_DIR=self.storage_dir,
            EDC_LAB_RESULTS_IMPORT_UPLOAD_DIR=upload_dir,
        ):
            self.assertEqual(
                error_ids(upload_and_storage_dirs_check(None)),
                ["edc_lab_results_import.E008"],
            )

    def test_check_storage_dir_inside_upload_dir_is_allowed(self):
        """Only the upload folder inside the storage folder is an error."""
        storage_dir = Path(self.upload_dir) / "storage"
        storage_dir.mkdir()
        with override_settings(
            EDC_LAB_RESULTS_IMPORT_STORAGE_DIR=storage_dir,
            EDC_LAB_RESULTS_IMPORT_UPLOAD_DIR=self.upload_dir,
        ):
            self.assertEqual(upload_and_storage_dirs_check(None), [])


@tag("lab_results_import")
@patch(f"{MODULE}.get_parser")
@patch(f"{MODULE}.get_mappings", return_value={"UTESTIDS": {}, "UNITS": {}})
class TestResultImporterPath(TestCase):
    """`ResultImporter` reads from the upload folder unless given a path.

    Mappings and parser are patched, they need laboratory-specific files.
    """

    def setUp(self):
        self.upload_dir = tempfile.mkdtemp()

    def test_defaults_to_upload_dir(self, *mocks):  # noqa: ARG002
        with override_settings(EDC_LAB_RESULTS_IMPORT_UPLOAD_DIR=self.upload_dir):
            importer = ResultImporter("MNH")
        self.assertEqual(importer.path, Path(self.upload_dir))

    def test_explicit_path(self, *mocks):  # noqa: ARG002
        folder = tempfile.mkdtemp()
        with override_settings(EDC_LAB_RESULTS_IMPORT_UPLOAD_DIR=self.upload_dir):
            importer = ResultImporter("MNH", folder)
        self.assertEqual(importer.path, Path(folder))

    def test_explicit_path_not_a_folder(self, *mocks):  # noqa: ARG002
        missing = str(Path(self.upload_dir) / "missing")
        self.assertRaises(ResultImporterError, ResultImporter, "MNH", missing)

    @override_settings(EDC_LAB_RESULTS_IMPORT_UPLOAD_DIR=None)
    def test_upload_dir_not_set(self, *mocks):  # noqa: ARG002
        self.assertRaises(EdcLabResultsUploadDirError, ResultImporter, "MNH")
