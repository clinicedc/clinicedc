from clinicedc_constants import DM, HIV
from django.test import TestCase, override_settings, tag

from edc_dx import get_diagnosis_labels_prefixes


@tag("dx")
class TestLabels(TestCase):
    @override_settings(EDC_DX_LABELS={HIV: "HIV"})
    def test_diagnosis_labels_hiv_only(self):
        self.assertEqual([x.lower() for x in [HIV]], get_diagnosis_labels_prefixes())

    @override_settings(EDC_DX_LABELS={HIV: "HIV", DM: "Diabetes"})
    def test_diagnosis_labels_hiv_dm_only(self):
        self.assertEqual([x.lower() for x in [HIV, DM]], get_diagnosis_labels_prefixes())
