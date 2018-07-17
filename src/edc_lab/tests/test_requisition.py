import re

from django.test import TestCase, tag
from edc_base.sites.utils import add_or_update_django_sites

from ..identifiers import RequisitionIdentifier
from ..lab import AliquotType, LabProfile, ProcessingProfile, RequisitionPanel, Process
from ..site_labs import site_labs


class TestRequisition(TestCase):

    @classmethod
    def setUpClass(cls):
        add_or_update_django_sites(
            sites=((10, 'test_site', 'Test Site'), ), fqdn='clinicedc.org')
        return super().setUpClass()

    def tearDown(self):
        super().tearDown()

    def test_requisition_identifier(self):
        """Asserts requisition identifier class creates identifier
        with correct format.
        """
        identifier = RequisitionIdentifier()
        pattern = re.compile('[0-9]{2}[A-Z0-9]{5}')
        self.assertTrue(pattern.match(str(identifier)))


class TestRequisitionModel(TestCase):

    @classmethod
    def setUpClass(cls):
        add_or_update_django_sites(
            sites=((10, 'test_site', 'Test Site'), ), fqdn='clinicedc.org')
        return super().setUpClass()

    def tearDown(self):
        super().tearDown()

    def setUp(self):
        self.requisition_model = 'edc_lab.subjectrequisition'
        a = AliquotType(name='aliquot_a', numeric_code='55', alpha_code='AA')
        b = AliquotType(name='aliquot_b', numeric_code='66', alpha_code='BB')
        a.add_derivatives(b)
        process = Process(aliquot_type=b, aliquot_count=3)
        processing_profile = ProcessingProfile(
            name='process', aliquot_type=a)
        processing_profile.add_processes(process)
        panel = RequisitionPanel(
            name='Viral Load',
            processing_profile=processing_profile)
        self.lab_profile = LabProfile(
            name='profile', requisition_model=self.requisition_model)
        self.lab_profile.add_panel(panel=panel)
        site_labs._registry = {}
        site_labs.loaded = False
        site_labs.register(lab_profile=self.lab_profile)

    def test_(self):
        obj = site_labs.get(lab_profile_name='profile')
        self.assertEqual(obj, self.lab_profile)

    def test_lab_profile_model(self):
        obj = site_labs.get(lab_profile_name='profile')
        self.assertEqual(self.requisition_model, obj.requisition_model)

    def test_panel_model(self):
        for panel in site_labs.get(lab_profile_name='profile').panels.values():
            self.assertEqual(panel.requisition_model, self.requisition_model)
