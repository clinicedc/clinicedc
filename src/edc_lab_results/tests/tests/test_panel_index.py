from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase, override_settings, tag

from edc_lab_results.import_results import LabResultImporter


def _fake_site_labs():
    """A registered profile with a single 'fbc' panel."""
    fbc = SimpleNamespace(name="fbc", utest_ids=("haemoglobin", "wbc"))
    profile = SimpleNamespace(panels={"fbc": fbc})
    return SimpleNamespace(lab_profiles={"subject": profile})


@tag("lab_results")
class TestPanelIndexGrouping(TestCase):
    """EDC_LAB_RESULTS_UTEST_PANELS attaches extra utest_ids to a registered
    panel so they link instead of being untracked."""

    def test_base_index_from_site_labs(self):
        with patch("edc_lab_results.import_results.site_labs", _fake_site_labs()):
            index = LabResultImporter._build_utest_id_panel_index()
        self.assertEqual(index["haemoglobin"], {"fbc"})
        self.assertEqual(index["wbc"], {"fbc"})
        self.assertNotIn("mono%", index)

    def test_extra_utest_panel_attaches_to_registered_panel(self):
        with (
            patch("edc_lab_results.import_results.site_labs", _fake_site_labs()),
            override_settings(EDC_LAB_RESULTS_UTEST_PANELS={"mono%": "fbc"}),
        ):
            index = LabResultImporter._build_utest_id_panel_index()
        self.assertEqual(index["mono%"], {"fbc"})

    def test_extra_utest_panel_ignored_when_unregistered(self):
        with (
            patch("edc_lab_results.import_results.site_labs", _fake_site_labs()),
            override_settings(EDC_LAB_RESULTS_UTEST_PANELS={"mono%": "haematology"}),
        ):
            index = LabResultImporter._build_utest_id_panel_index()
        self.assertNotIn("mono%", index)
