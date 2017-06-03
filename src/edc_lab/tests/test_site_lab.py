import re

from django.test import TestCase, tag

from edc_constants.constants import YES, NO

from ..lab import AliquotType, LabProfile, ProcessingProfile, RequisitionPanel
from ..lab import Process
from ..site_labs import SiteLabs, site_labs
from .models import SubjectRequisition, SubjectVisit


@tag('site')
class TestSiteLab(TestCase):

    def test_site_labs(self):
        site_lab = SiteLabs()
        self.assertFalse(site_lab.loaded)

    def test_site_labs_register(self):
        lab_profile = LabProfile(
            name='lab_profile',
            requisition_model=SubjectRequisition)
        site_lab = SiteLabs()
        site_lab.register(lab_profile)
        self.assertTrue(site_lab.loaded)

    def test_site_labs_register_none(self):
        site_lab = SiteLabs()
        site_lab.register(None)
        self.assertFalse(site_lab.loaded)


@tag('site')
class TestSiteLab2(TestCase):

    def setUp(self):
        site_labs._registry = {}

        # create aliquots and their relationship
        a = AliquotType(name='aliquot_a')
        b = AliquotType(name='aliquot_b')
        a.add_derivatives(b)

        # set up processes
        process = Process(aliquot_type=b, aliquot_count=3)
        processing_profile = ProcessingProfile(
            name='process', aliquot_type=a)
        processing_profile.add_processes(process)

        # create a panel
        self.panel = RequisitionPanel(
            name='panel',
            model=SubjectRequisition,
            aliquot_type=a,
            processing_profile=processing_profile)

        # lab profile
        self.lab_profile = LabProfile(
            name='lab_profile',
            requisition_model=SubjectRequisition)
        self.lab_profile.add_panel(self.panel)

        # register with site
        site_labs.register(self.lab_profile)

    def test_site_lab_panels(self):
        self.assertIn(
            self.panel.name,
            site_labs.get(self.lab_profile.name).panels)

    def test_requisition_specimen(self):
        """Asserts can create a requisition.
        """
        subject_visit = SubjectVisit.objects.create()
        SubjectRequisition.objects.create(
            subject_visit=subject_visit,
            panel_name=self.panel.name)

    def test_requisition_identifier2(self):
        """Asserts requisition identifier is set on requisition.
        """
        subject_visit = SubjectVisit.objects.create()
        requisition = SubjectRequisition.objects.create(
            subject_visit=subject_visit,
            panel_name=self.panel.name,
            is_drawn=YES)
        pattern = re.compile('[0-9]{2}[A-Z0-9]{5}')
        self.assertTrue(pattern.match(requisition.requisition_identifier))

    def test_requisition_identifier3(self):
        """Asserts requisition identifier is NOT set on requisition
        if specimen not drawn.
        """
        subject_visit = SubjectVisit.objects.create()
        requisition = SubjectRequisition.objects.create(
            subject_visit=subject_visit,
            panel_name=self.panel.name,
            is_drawn=NO)
        pattern = re.compile('[0-9]{2}[A-Z0-9]{5}')
        self.assertFalse(pattern.match(requisition.requisition_identifier))

    def test_requisition_identifier4(self):
        """Asserts requisition identifier is CLEARED if specimen
        changed to not drawn."""
        subject_visit = SubjectVisit.objects.create()
        requisition = SubjectRequisition.objects.create(
            subject_visit=subject_visit,
            panel_name=self.panel.name,
            is_drawn=YES)
        requisition.is_drawn = NO
        requisition.save()
        pattern = re.compile('[0-9]{2}[A-Z0-9]{5}')
        self.assertFalse(pattern.match(requisition.requisition_identifier))

    def test_requisition_identifier5(self):
        """Asserts requisition identifier is set if specimen changed to drawn."""
        subject_visit = SubjectVisit.objects.create()
        requisition = SubjectRequisition.objects.create(
            subject_visit=subject_visit,
            panel_name=self.panel.name,
            is_drawn=NO)
        requisition.is_drawn = YES
        requisition.save()
        pattern = re.compile('[0-9]{2}[A-Z0-9]{5}')
        self.assertTrue(pattern.match(requisition.requisition_identifier))

    def test_requisition_identifier6(self):
        """Asserts requisition identifier is unchanged on save/resave."""
        subject_visit = SubjectVisit.objects.create()
        requisition = SubjectRequisition.objects.create(
            subject_visit=subject_visit,
            panel_name=self.panel.name,
            is_drawn=YES)
        requisition_identifier = requisition.requisition_identifier
        requisition.is_drawn = YES
        requisition.save()
        self.assertEqual(
            requisition_identifier, requisition.requisition_identifier)
