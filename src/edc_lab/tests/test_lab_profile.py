from django.test import TestCase, tag

from ..lab import AliquotType, LabProfile, ProcessingProfile, RequisitionPanel
from ..lab import PanelAlreadyRegistered, ProcessingProfileInvalidDerivative
from ..lab import RequisitionPanelError, Process, InvalidProcessingProfile
from ..lab import RequisitionPanelModelError


class TestBuildProfile(TestCase):

    def setUp(self):
        self.wb = AliquotType(
            name='whole_blood', numeric_code='02', alpha_code='WB')
        self.bc = AliquotType(
            name='buffy_coat', numeric_code='12', alpha_code='BC')

    def test_repr(self):
        obj = LabProfile(
            name='profile', requisition_model='edc_lab.subjectrequisition')
        self.assertTrue(repr(obj))

    def test_str(self):
        obj = LabProfile(
            name='profile', requisition_model='edc_lab.subjectrequisition')
        self.assertTrue(str(obj))

    def test_processing_bad(self):
        """Asserts CANNOT add process for aliquot B to a profile
        for aliquot A if B cannot be derived from A."""
        a = AliquotType(name='aliquot_a', numeric_code='55', alpha_code='AA')
        b = AliquotType(name='aliquot_b', numeric_code='66', alpha_code='BB')
        process = Process(aliquot_type=b, aliquot_count=3)
        processing_profile = ProcessingProfile(
            name='process', aliquot_type=a)
        self.assertRaises(
            ProcessingProfileInvalidDerivative,
            processing_profile.add_processes, process)

    def test_processing_ok(self):
        """Asserts CAN add process for aliquot B to a profile
        for aliquot A since B can be derived from A."""
        a = AliquotType(name='aliquot_a', numeric_code='55', alpha_code='AA')
        b = AliquotType(name='aliquot_b', numeric_code='66', alpha_code='BB')
        a.add_derivatives(b)
        process = Process(aliquot_type=b, aliquot_count=3)
        processing_profile = ProcessingProfile(
            name='process', aliquot_type=a)
        try:
            processing_profile.add_processes(process)
        except ProcessingProfileInvalidDerivative:
            self.fail('ProcessingProfileInvalidDerivative unexpectedly raised.')

    def test_panel(self):
        RequisitionPanel(name='Viral Load', aliquot_type=self.bc)

    def test_panel_raises_missing_aliquot_type(self):
        self.assertRaises(
            RequisitionPanelError,
            RequisitionPanel,
            name='Viral Load',
            aliquot_type=None)

    def test_panel_raises_on_invalid_model(self):
        a = AliquotType(name='aliquot_a', numeric_code='55', alpha_code='AA')
        for requisition_model in [None, 'edc_lab.blah', 'blah']:
            with self.subTest(requisition_model=requisition_model):
                panel = RequisitionPanel(
                    name='Viral Load',
                    aliquot_type=a)
                panel.requisition_model = requisition_model
                try:
                    panel.requisition_model_cls
                except RequisitionPanelModelError:
                    pass
                else:
                    self.fail(
                        'RequisitionPanelModelError unexpectedly not raised.')

    def test_panel_adds_processing_profile(self):
        a = AliquotType(name='aliquot_a', numeric_code='55', alpha_code='AA')
        b = AliquotType(name='aliquot_b', numeric_code='66', alpha_code='BB')
        a.add_derivatives(b)
        process = Process(aliquot_type=b, aliquot_count=3)
        processing_profile = ProcessingProfile(
            name='process', aliquot_type=a)
        processing_profile.add_processes(process)
        RequisitionPanel(
            name='Viral Load',
            aliquot_type=a,
            processing_profile=processing_profile)

    def test_panel_adding_processing_profile_raises(self):
        """Asserts CANNOT add processing profile for aliquot type B
        to panel for aliquot type C.
        """
        a = AliquotType(name='aliquot_a', numeric_code='55', alpha_code='AA')
        b = AliquotType(name='aliquot_b', numeric_code='66', alpha_code='BB')
        c = AliquotType(name='aliquot_c', numeric_code='77', alpha_code='CC')
        a.add_derivatives(b)
        process = Process(aliquot_type=b, aliquot_count=3)
        processing_profile = ProcessingProfile(
            name='process', aliquot_type=a)
        processing_profile.add_processes(process)
        self.assertRaises(
            InvalidProcessingProfile,
            RequisitionPanel,
            name='Viral Load',
            aliquot_type=c,
            processing_profile=processing_profile)

    def test_add_processesing(self):
        a = AliquotType(name='aliquot_a', numeric_code='55', alpha_code='AA')
        b = AliquotType(name='aliquot_b', numeric_code='66', alpha_code='BB')
        a.add_derivatives(b)
        process = Process(aliquot_type=b, aliquot_count=3)
        processing_profile = ProcessingProfile(
            name='process', aliquot_type=a)
        processing_profile.add_processes(process)
        panel = RequisitionPanel(
            name='Viral Load',
            aliquot_type=a,
            processing_profile=processing_profile)
        lab_profile = LabProfile(
            name='profile', requisition_model='edc_lab.subjectrequisition')
        lab_profile.add_panel(panel=panel)

    def test_add_panel(self):
        a = AliquotType(name='aliquot_a', numeric_code='55', alpha_code='AA')
        b = AliquotType(name='aliquot_b', numeric_code='66', alpha_code='BB')
        a.add_derivatives(b)
        process = Process(aliquot_type=b, aliquot_count=3)
        processing_profile = ProcessingProfile(
            name='process', aliquot_type=a)
        processing_profile.add_processes(process)
        panel = RequisitionPanel(
            name='Viral Load',
            aliquot_type=a,
            processing_profile=processing_profile)
        lab_profile = LabProfile(
            name='profile', requisition_model='edc_lab.subjectrequisition')
        lab_profile.add_panel(panel=panel)
        self.assertRaises(
            PanelAlreadyRegistered,
            lab_profile.add_panel, panel=panel)
