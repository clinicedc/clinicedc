from clinicedc_tests.models import BloodResultsFbc
from django.test import TestCase, tag

from edc_lab_results.utils import get_result_model_cls, get_result_models_by_panel_name


@tag("lab_results")
class TestResultModelsByPanelName(TestCase):
    def test_maps_panel_name_to_result_crf(self):
        self.assertEqual(BloodResultsFbc, get_result_model_cls("fbc"))

    def test_unknown_panel_name_returns_none(self):
        self.assertIsNone(get_result_model_cls("blah"))
        self.assertIsNone(get_result_model_cls(""))
        self.assertIsNone(get_result_model_cls(None))

    def test_excludes_models_not_linked_to_a_requisition(self):
        """`clinicedc_tests.ResultCrf` declares `lab_panel` but is not a
        `CrfWithRequisitionModelMixin`, so it is not a result CRF.
        """
        self.assertIsNone(get_result_model_cls("chemistry_rft"))

    def test_panel_name_is_read_from_the_model(self):
        registry = get_result_models_by_panel_name()
        self.assertIn("fbc", registry)
        for panel_name, model_cls in registry.items():
            self.assertEqual(panel_name, model_cls.lab_panel.name)
