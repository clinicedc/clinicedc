from django.test import TestCase, tag

from ..lab import AliquotType, LabProfile, ProcessingProfile, RequisitionPanel
from ..lab import PanelAlreadyRegistered, ProcessingProfileInvalidDerivative
from ..lab import RequisitionPanelError, Process, InvalidProcessingProfile
from ..lab import RequisitionPanelModelError
from ..site_labs import site_labs


@tag('profile')
class TestBuildProfile(TestCase):

    def setUp(self):
        self.wb = AliquotType(
            name='whole_blood', numeric_code='02', alpha_code='WB')
        self.bc = AliquotType(
            name='buffy_coat', numeric_code='12', alpha_code='BC')

    def test_repr(self):
        obj = LabProfile(name='profile')
        self.assertTrue(repr(obj))

    def test_str(self):
        obj = LabProfile(name='profile')
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
        for model in [None, 'edc_lab.blah', 'blah']:
            with self.subTest(model=model):
                req = RequisitionPanel(
                    name='Viral Load',
                    aliquot_type=a)
                req.model = model
                try:
                    req.model_cls
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
        lab_profile = LabProfile(name='profile')
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
        lab_profile = LabProfile(name='profile')
        lab_profile.add_panel(panel=panel)
        self.assertRaises(
            PanelAlreadyRegistered,
            lab_profile.add_panel, panel=panel)


class TestRequisitionModel(TestCase):

    def setUp(self):
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
        self.lab_profile = LabProfile(name='profile')
        self.lab_profile.add_panel(panel=panel)
        site_labs._registry = {}
        site_labs.loaded = False
        site_labs.register(
            lab_profile=self.lab_profile,
            requisition_model='edc_lab.subjectrequisition')

    def test_(self):
        obj = site_labs.get(lab_profile_name='profile')
        self.assertEqual(obj, self.lab_profile)

    def test_lab_profile_model(self):
        obj = site_labs.get(lab_profile_name='profile')
        self.assertEqual('edc_lab.subjectrequisition',
                         obj.requisition_model)

    def test_panel_model(self):
        for panel in site_labs.get(lab_profile_name='profile').panels.values():
            self.assertEqual(panel.model, 'edc_lab.subjectrequisition')
