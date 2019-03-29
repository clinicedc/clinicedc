from django.test import TestCase, tag
from edc_lab.lab import AliquotType, LabProfile, ProcessingProfile, RequisitionPanel
from edc_lab.lab import PanelAlreadyRegistered, ProcessingProfileInvalidDerivative
from edc_lab.lab import Process

from ..models import SubjectRequisition


class TestBuildProfile(TestCase):
    def setUp(self):
        self.wb = AliquotType(name="whole_blood", numeric_code="02", alpha_code="WB")
        self.bc = AliquotType(name="buffy_coat", numeric_code="12", alpha_code="BC")

    def test_repr(self):
        obj = LabProfile(name="profile", requisition_model="edc_lab.subjectrequisition")
        self.assertTrue(repr(obj))

    def test_str(self):
        obj = LabProfile(name="profile", requisition_model="edc_lab.subjectrequisition")
        self.assertTrue(str(obj))

    def test_processing_bad(self):
        """Asserts CANNOT add process for aliquot B to a profile
        for aliquot A if B cannot be derived from A.
        """
        a = AliquotType(name="aliquot_a", numeric_code="55", alpha_code="AA")
        b = AliquotType(name="aliquot_b", numeric_code="66", alpha_code="BB")
        process = Process(aliquot_type=b, aliquot_count=3)
        processing_profile = ProcessingProfile(name="process", aliquot_type=a)
        self.assertRaises(
            ProcessingProfileInvalidDerivative,
            processing_profile.add_processes,
            process,
        )

    def test_processing_ok(self):
        """Asserts CAN add process for aliquot B to a profile
        for aliquot A since B can be derived from A.
        """
        a = AliquotType(name="aliquot_a", numeric_code="55", alpha_code="AA")
        b = AliquotType(name="aliquot_b", numeric_code="66", alpha_code="BB")
        a.add_derivatives(b)
        process = Process(aliquot_type=b, aliquot_count=3)
        processing_profile = ProcessingProfile(name="process", aliquot_type=a)
        try:
            processing_profile.add_processes(process)
        except ProcessingProfileInvalidDerivative:
            self.fail("ProcessingProfileInvalidDerivative unexpectedly raised.")

    def test_panel_adds_processing_profile(self):
        a = AliquotType(name="aliquot_a", numeric_code="55", alpha_code="AA")
        b = AliquotType(name="aliquot_b", numeric_code="66", alpha_code="BB")
        a.add_derivatives(b)
        process = Process(aliquot_type=b, aliquot_count=3)
        processing_profile = ProcessingProfile(name="process", aliquot_type=a)
        processing_profile.add_processes(process)
        panel = RequisitionPanel(
            name="some panel", processing_profile=processing_profile
        )
        lab_profile = LabProfile(
            name="profile", requisition_model="edc_lab.subjectrequisition"
        )
        lab_profile.add_panel(panel=panel)
        self.assertEqual(panel, lab_profile.panels.get(panel.name))

    def test_add_processing(self):
        a = AliquotType(name="aliquot_a", numeric_code="55", alpha_code="AA")
        b = AliquotType(name="aliquot_b", numeric_code="66", alpha_code="BB")
        a.add_derivatives(b)
        process = Process(aliquot_type=b, aliquot_count=3)
        processing_profile = ProcessingProfile(name="process", aliquot_type=a)
        processing_profile.add_processes(process)
        panel = RequisitionPanel(
            name="Viral Load", processing_profile=processing_profile
        )
        lab_profile = LabProfile(
            name="profile", requisition_model="edc_lab.subjectrequisition"
        )
        lab_profile.add_panel(panel=panel)

    def test_add_panel(self):
        """Assert same panel cannot be added twice.
        """
        a = AliquotType(name="aliquot_a", numeric_code="55", alpha_code="AA")
        b = AliquotType(name="aliquot_b", numeric_code="66", alpha_code="BB")
        a.add_derivatives(b)
        process = Process(aliquot_type=b, aliquot_count=3)
        processing_profile = ProcessingProfile(name="process", aliquot_type=a)
        processing_profile.add_processes(process)
        panel = RequisitionPanel(
            name="Viral Load", processing_profile=processing_profile
        )
        lab_profile = LabProfile(
            name="profile", requisition_model="edc_lab.subjectrequisition"
        )
        lab_profile.add_panel(panel=panel)
        self.assertRaises(PanelAlreadyRegistered, lab_profile.add_panel, panel=panel)

    def test_added_panel_knows_requisition_model(self):
        """Assert same panel cannot be added twice.
        """
        a = AliquotType(name="aliquot_a", numeric_code="55", alpha_code="AA")
        b = AliquotType(name="aliquot_b", numeric_code="66", alpha_code="BB")
        a.add_derivatives(b)
        process = Process(aliquot_type=b, aliquot_count=3)
        processing_profile = ProcessingProfile(name="process", aliquot_type=a)
        processing_profile.add_processes(process)
        panel = RequisitionPanel(
            name="Viral Load", processing_profile=processing_profile
        )
        lab_profile = LabProfile(
            name="profile", requisition_model="edc_lab.subjectrequisition"
        )
        lab_profile.add_panel(panel=panel)
        panel = lab_profile.panels.get("Viral Load")
        self.assertEqual(panel.requisition_model, "edc_lab.subjectrequisition")
        self.assertEqual(panel.requisition_model_cls, SubjectRequisition)
