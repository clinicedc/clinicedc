from tempfile import mkdtemp
from types import SimpleNamespace

from clinicedc_tests.sites import all_sites
from django.contrib.auth.models import User
from django.test import TestCase, override_settings, tag

from edc_export.utils import record_cli_export_audit
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites

ARCHIVE_PATH = "/exports/archive.zip"


def _fake_models_to_file(**overrides) -> SimpleNamespace:
    """Minimal stand-in for ModelsToFile — we only touch the attributes
    that record_cli_export_audit reads.
    """
    defaults = dict(
        models=["edc_export.datarequest", "edc_export.datarequesthistory"],
        exported_filenames=["a.csv", "b.csv"],
        archive_filename=ARCHIVE_PATH,
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


@tag("export")
@override_settings(
    EDC_EXPORT_EXPORT_FOLDER=mkdtemp(),
    EDC_AUTH_SKIP_AUTH_UPDATER=True,
    EDC_AUTH_SKIP_SITE_AUTHS=True,
    SITE_ID=10,
)
class TestRecordCliExportAudit(TestCase):
    @classmethod
    def setUpTestData(cls):
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

    def setUp(self):
        self.user = User.objects.create(username="alice")

    def test_creates_data_request_and_history(self):
        data_request, history = record_cli_export_audit(
            user=self.user,
            models_to_file=_fake_models_to_file(),
            decrypt=False,
            export_format="csv",
            export_path="/var/exports",
        )
        self.assertEqual(data_request.user_created, "alice")
        self.assertIn("edc_export.datarequest", data_request.models)
        self.assertIn("edc_export.datarequesthistory", data_request.models)
        self.assertFalse(data_request.decrypt)
        self.assertEqual(history.data_request_id, data_request.id)
        self.assertEqual(history.archive_filename, ARCHIVE_PATH)
        self.assertIn("a.csv", history.summary)
        self.assertIn("b.csv", history.summary)

    def test_summary_is_sorted(self):
        _, history = record_cli_export_audit(
            user=self.user,
            models_to_file=_fake_models_to_file(
                exported_filenames=["z.csv", "a.csv", "m.csv"]
            ),
            decrypt=False,
            export_format="csv",
        )
        self.assertEqual(history.summary.splitlines(), ["a.csv", "m.csv", "z.csv"])

    def test_description_records_filters(self):
        data_request, _ = record_cli_export_audit(
            user=self.user,
            models_to_file=_fake_models_to_file(),
            decrypt=True,
            export_format=118,
            site_ids=[10, 20],
            countries=["uganda"],
            trial_prefix="effect",
            include_historical=True,
            export_path="/exports",
        )
        desc = data_request.description
        self.assertIn("export_models", desc)
        self.assertIn("decrypt=True", desc)
        self.assertIn("include_historical=True", desc)
        self.assertIn("trial_prefix=effect", desc)
        self.assertIn("site_ids=10,20", desc)
        self.assertIn("countries=uganda", desc)
        self.assertIn("export_path=/exports", desc)
        self.assertIn("export_format=118", desc)

    def test_empty_exported_filenames_is_handled(self):
        """Defensive: should not crash if the exporter produced no files."""
        _, history = record_cli_export_audit(
            user=self.user,
            models_to_file=_fake_models_to_file(exported_filenames=[]),
            decrypt=False,
            export_format="csv",
        )
        self.assertEqual(history.summary, "")

    def test_name_has_timestamp_prefix(self):
        data_request, _ = record_cli_export_audit(
            user=self.user,
            models_to_file=_fake_models_to_file(),
            decrypt=False,
            export_format="csv",
        )
        self.assertTrue(data_request.name.startswith("CLI export "))
