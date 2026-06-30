import shutil
from pathlib import Path
from tempfile import mkdtemp

import pandas as pd
from clinicedc_tests.sites import all_sites
from clinicedc_tests.utils import get_user_for_tests
from django.contrib.sites.models import Site
from django.test import TestCase
from django.test.utils import override_settings, tag

from edc_export.constants import CSV, STATA_14
from edc_export.models_to_file import ModelsToFile, ModelsToFileNothingExportedError
from edc_facility.import_holidays import import_holidays
from edc_registration.models import RegisteredSubject
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites


@tag("export")
@override_settings(
    EDC_EXPORT_EXPORT_FOLDER=mkdtemp(), EDC_EXPORT_UPLOAD_FOLDER=mkdtemp(), SITE_ID=10
)
class TestArchiveExporter(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

    def setUp(self):
        self.user = get_user_for_tests(username="erikvw")
        Site.objects.get_current()
        RegisteredSubject.objects.create(subject_identifier="12345")
        self.models = ["auth.user", "edc_registration.registeredsubject"]

    def test_request_archive(self):
        exporter = ModelsToFile(
            models=self.models, user=self.user, archive_to_single_file=True, export_format=CSV
        )
        folder = Path(mkdtemp())
        shutil.unpack_archive(exporter.archive_filename, folder, "zip")
        filenames = [f for f in folder.iterdir()]
        self.assertGreater(len([f for f in filenames]), 0)

    def test_request_archive_filename_exists(self):
        exporter = ModelsToFile(
            models=self.models, user=self.user, archive_to_single_file=True, export_format=CSV
        )
        filename = Path(exporter.archive_filename)
        self.assertIsNotNone(filename)
        self.assertTrue(filename.exists(), msg=f"file '{filename}' does not exist")

    def test_request_archive_stata(self):
        """A STATA export must not raise on UUID pk/fk columns.

        Regression: the 'id' and '*_id' columns arrive as uuid.UUID objects
        (object dtype) and 'last_login' (auth.user) is all-null. to_stata
        rejects object columns that are not all strings/None, so without
        coercion this raised "ValueError: Column `id` cannot be exported".
        """
        exporter = ModelsToFile(
            models=self.models,
            user=self.user,
            archive_to_single_file=True,
            export_format=STATA_14,
        )
        folder = Path(mkdtemp())
        shutil.unpack_archive(exporter.archive_filename, folder, "zip")
        dta_files = list(folder.rglob("*.dta"))
        self.assertGreater(len(dta_files), 0, msg="no .dta files were exported")
        # the exported file must be readable back and carry the uuid pk as string
        registeredsubject_dta = next(
            f for f in dta_files if "registeredsubject" in f.name.lower()
        )
        df = pd.read_stata(registeredsubject_dta)
        self.assertIn("id", df.columns)
        # the uuid pk must round-trip as a non-null string, not a uuid object
        self.assertTrue(df["id"].notna().all())
        self.assertIsInstance(df["id"].iloc[0], str)

    def test_requested_with_invalid_table(self):
        models = ["auth.blah", "edc_registration.registeredsubject"]
        self.assertRaises(
            LookupError,
            ModelsToFile,
            models=models,
            user=self.user,
            archive_to_single_file=True,
            export_format=CSV,
        )

    def test_requested_with_nothing(self):
        self.assertRaises(
            ModelsToFileNothingExportedError,
            ModelsToFile,
            models=[],
            user=self.user,
            archive_to_single_file=True,
            export_format=CSV,
        )
