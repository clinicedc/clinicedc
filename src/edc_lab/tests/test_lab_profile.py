from django.test import TestCase, tag

from ..lab import AliquotType, LabProfile, ProcessingProfile, RequisitionPanel
from ..lab import PanelAlreadyRegistered, ProcessingProfileInvalidDerivative
from ..lab import RequisitionPanelError, Process, InvalidProcessingProfile, RequisitionModelError
from .models import SubjectRequisition


@tag('profile')
class TestBuildProfile(TestCase):

    def test_repr(self):
        obj = LabProfile(name='profile')
        self.assertTrue(repr(obj))

    def test_str(self):
        obj = LabProfile(name='profile')
        self.assertTrue(str(obj))

    def test_aliquot_derivatives_single(self):
        """Asserts can add a derivative.
        """
        wb = AliquotType(name='whole_blood')
        bc = AliquotType(name='buffy_coat')
        wb.add_derivatives(bc)
        self.assertEqual(wb.derivatives, [bc])

    def test_aliquot_derivatives_multi(self):
        """Asserts can add more than one derivative.
        """
        wb = AliquotType(name='whole_blood')
        bc = AliquotType(name='buffy_coat')
        pl = AliquotType(name='plasma')
        wb.add_derivatives(bc, pl)
        self.assertEqual(wb.derivatives, [bc, pl])

    def test_processing_bad(self):
        """Asserts CANNOT add process for aliquot B to a profile
        for aliquot A if B cannot be derived from A."""
        a = AliquotType(name='aliquot_a')
        b = AliquotType(name='aliquot_b')
        process = Process(aliquot_type=b, aliquot_count=3)
        processing_profile = ProcessingProfile(
            name='process', aliquot_type=a)
        self.assertRaises(
            ProcessingProfileInvalidDerivative,
            processing_profile.add_processes, process=process)

    def test_processing_ok(self):
        """Asserts CAN add process for aliquot B to a profile
        for aliquot A since B can be derived from A."""
        a = AliquotType(name='aliquot_a')
        b = AliquotType(name='aliquot_b')
        a.add_derivatives(b)
        process = Process(aliquot_type=b, aliquot_count=3)
        processing_profile = ProcessingProfile(
            name='process', aliquot_type=a)
        try:
            processing_profile.add_processes(process)
        except ProcessingProfileInvalidDerivative:
            self.fail('ProcessingProfileInvalidDerivative unexpectedly raised.')

    def test_panel(self):
        aliquot_type = AliquotType(name='buffy_coat')
        RequisitionPanel(name='Viral Load', aliquot_type=aliquot_type)

    def test_panel_raises_missing_aliquot_type(self):
        self.assertRaises(
            RequisitionPanelError,
            RequisitionPanel,
            name='Viral Load',
            aliquot_type=None,
            model='edc_lab.subjectrequisition')

    def test_panel_raises_on_invalid_model(self):
        a = AliquotType(name='aliquot_a')
        for model in [None, 'edc_lab.blah', 'blah']:
            with self.subTest(model=model):
                req = RequisitionPanel(
                    name='Viral Load',
                    aliquot_type=a,
                    model=model)
                try:
                    req.model
                except RequisitionModelError:
                    pass
                else:
                    self.fail('RequisitionModelError unexpectedly not raised.')

    def test_panel_accepts_model_as_a_class(self):
        a = AliquotType(name='aliquot_a')
        try:
            RequisitionPanel(
                name='Viral Load',
                aliquot_type=a,
                model=SubjectRequisition).model
        except RequisitionModelError:
            self.fail('RequisitionModelError unexpectedly raised.')

    def test_panel_adds_processing_profile(self):
        a = AliquotType(name='aliquot_a')
        b = AliquotType(name='aliquot_b')
        a.add_derivatives(b)
        process = Process(aliquot_type=b, aliquot_count=3)
        processing_profile = ProcessingProfile(
            name='process', aliquot_type=a)
        processing_profile.add_processes(process)
        RequisitionPanel(
            name='Viral Load',
            aliquot_type=a,
            model='edc_lab.subjectrequisition',
            processing_profile=processing_profile)

    def test_panel_adding_processing_profile_raises(self):
        """Asserts CANNOT add processing profile for aliquot type B
        to panel for aliquot type C.
        """
        a = AliquotType(name='aliquot_a')
        b = AliquotType(name='aliquot_b')
        c = AliquotType(name='aliquot_c')
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
            processing_profile=processing_profile,
            model='edc_lab.subjectrequisition')

    def test_add_processesing(self):
        a = AliquotType(name='aliquot_a')
        b = AliquotType(name='aliquot_b')
        a.add_derivatives(b)
        process = Process(aliquot_type=b, aliquot_count=3)
        processing_profile = ProcessingProfile(
            name='process', aliquot_type=a)
        processing_profile.add_processes(process)
        panel = RequisitionPanel(
            name='Viral Load',
            aliquot_type=a,
            model='edc_lab.subjectrequisition',
            processing_profile=processing_profile)
        lab_profile = LabProfile(
            name='profile',
            requisition_model='edc_lab.subjectrequisition')
        lab_profile.add_panel(panel=panel)

    def test_add_panel(self):
        a = AliquotType(name='aliquot_a')
        b = AliquotType(name='aliquot_b')
        a.add_derivatives(b)
        process = Process(aliquot_type=b, aliquot_count=3)
        processing_profile = ProcessingProfile(
            name='process', aliquot_type=a)
        processing_profile.add_processes(process)
        panel = RequisitionPanel(
            name='Viral Load',
            aliquot_type=a,
            model='edc_lab.subjectrequisition',
            processing_profile=processing_profile)
        lab_profile = LabProfile(
            name='profile',
            requisition_model='edc_lab.subjectrequisition')
        lab_profile.add_panel(panel=panel)
        self.assertRaises(
            PanelAlreadyRegistered,
            lab_profile.add_panel, panel=panel)
