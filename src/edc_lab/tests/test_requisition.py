import re

from django.test import TestCase, tag

from ..identifiers import RequisitionIdentifier
from ..site_labs import site_labs
from ..lab import AliquotType, LabProfile, ProcessingProfile, RequisitionPanel, Process


class TestRequisition(TestCase):

    def test_requisition_identifier(self):
        """Asserts requisition identifier class creates identifier
        with correct format.
        """
        identifier = RequisitionIdentifier()
        pattern = re.compile('[0-9]{2}[A-Z0-9]{5}')
        self.assertTrue(pattern.match(str(identifier)))


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
        self.lab_profile = LabProfile(
            name='profile', requisition_model='edc_lab.subjectrequisition')
        self.lab_profile.add_panel(panel=panel)
        site_labs._registry = {}
        site_labs.loaded = False
        site_labs.register(lab_profile=self.lab_profile)

    def test_(self):
        obj = site_labs.get(lab_profile_name='profile')
        self.assertEqual(obj, self.lab_profile)

    def test_lab_profile_model(self):
        obj = site_labs.get(lab_profile_name='profile')
        self.assertEqual('edc_lab.subjectrequisition',
                         obj.requisition_model)

    def test_panel_model(self):
        for panel in site_labs.get(lab_profile_name='profile').panels.values():
            self.assertEqual(panel.requisition_model,
                             'edc_lab.subjectrequisition')
