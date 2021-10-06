from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from edc_lab.lab import (
    AliquotType,
    LabProfile,
    ProcessingProfile,
    RequisitionPanel,
    RequisitionPanelLookupError,
)
from edc_lab.models import Panel
from edc_lab.site_labs import site_labs


class TestPanel(TestCase):
    def setUp(self):
        site_labs._registry = {}

    def test_panel(self):
        Panel.objects.create(
            name="panel", display_name="My Panel", lab_profile_name="lab_profile"
        )

    def test_panel2(self):

        wb = AliquotType(name="Whole Blood", alpha_code="WB", numeric_code="02")

        whole_blood_processing = ProcessingProfile(name="whole_blood_store", aliquot_type=wb)

        wb_panel = RequisitionPanel(
            name="wb_storage",
            verbose_name="Whole Blood Storage",
            processing_profile=whole_blood_processing,
        )

        lab_profile = LabProfile(
            name="test_profile", requisition_model="edc_lab.subjectrequisition"
        )
        lab_profile.add_panel(wb_panel)

        site_labs.register(lab_profile=lab_profile)

        try:
            Panel.objects.get(name="wb_storage")
        except ObjectDoesNotExist:
            self.fail("Panel unexpectedly does not exist")

        panel = Panel.objects.get(name="wb_storage")

        self.assertEqual(panel.display_name, "Whole Blood Storage")
        self.assertEqual(panel.lab_profile_name, "test_profile")

    def test_requisition_panel_str(self):
        a = AliquotType(name="aliquot_a", numeric_code="55", alpha_code="AA")
        processing_profile = ProcessingProfile(name="process", aliquot_type=a)
        panel = RequisitionPanel(name="Viral Load", processing_profile=processing_profile)
        self.assertTrue(str(panel))

    def test_requisition_panel(self):
        a = AliquotType(name="aliquot_a", numeric_code="55", alpha_code="AA")
        processing_profile = ProcessingProfile(name="process", aliquot_type=a)
        RequisitionPanel(name="Viral Load", processing_profile=processing_profile)

    def test_requisition_panel_does_not_know_requisition_model(self):
        """Demonstrate that a panel not yet added to a lab profile
        does not know the requisition model.
        """
        a = AliquotType(name="aliquot_a", numeric_code="55", alpha_code="AA")
        processing_profile = ProcessingProfile(name="process", aliquot_type=a)
        panel = RequisitionPanel(name="Viral Load", processing_profile=processing_profile)
        self.assertIsNone(panel.requisition_model)
        self.assertRaises(RequisitionPanelLookupError, getattr, panel, "requisition_model_cls")

    def test_requisition_panel_raises_on_invalid_requisition_model(self):
        a = AliquotType(name="aliquot_a", numeric_code="55", alpha_code="AA")
        processing_profile = ProcessingProfile(name="process", aliquot_type=a)
        for requisition_model in [None, "edc_lab.blah", "blah"]:
            with self.subTest(requisition_model=requisition_model):
                panel = RequisitionPanel(
                    name="Viral Load", processing_profile=processing_profile
                )
                # manually set, normally done by LabProfile
                panel.requisition_model = requisition_model
                try:
                    panel.requisition_model_cls
                except RequisitionPanelLookupError:
                    pass
                else:
                    self.fail("RequisitionPanelModelError unexpectedly not raised.")
