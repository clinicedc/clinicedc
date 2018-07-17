import re

from django.test import TestCase, tag
from edc_base.sites.utils import add_or_update_django_sites
from edc_constants.constants import YES, NO, NOT_APPLICABLE

from ..lab import AliquotType, LabProfile, ProcessingProfile
from ..lab import Process, ProcessingProfileAlreadyAdded
from ..site_labs import SiteLabs, site_labs
from .models import SubjectRequisition, SimpleSubjectVisit as SubjectVisit
from .site_labs_test_helper import SiteLabsTestHelper


class TestSiteLab(TestCase):

    @classmethod
    def setUpClass(cls):
        add_or_update_django_sites(
            sites=((10, 'test_site', 'Test Site'), ), fqdn='clinicedc.org')
        return super().setUpClass()

    def tearDown(self):
        super().tearDown()

    def test_site_labs(self):
        site_lab = SiteLabs()
        self.assertFalse(site_lab.loaded)

    def test_site_labs_register(self):
        lab_profile = LabProfile(
            name='lab_profile', requisition_model='edc_lab.subjectrequisition')
        site_lab = SiteLabs()
        site_lab.register(lab_profile)
        self.assertTrue(site_lab.loaded)

    def test_site_labs_register_none(self):
        site_lab = SiteLabs()
        site_lab.register(None)
        self.assertFalse(site_lab.loaded)


class TestSiteLab2(TestCase):

    lab_helper = SiteLabsTestHelper()

    def setUp(self):
        self.lab_helper.setup_site_labs()
        self.panel = self.lab_helper.panel
        self.lab_profile = self.lab_helper.lab_profile

    def test_site_lab_panels(self):
        self.assertIn(
            self.panel.name,
            site_labs.get(self.lab_profile.name).panels)

    def test_panel_repr(self):
        self.assertTrue(repr(self.panel))

    def test_assert_cannot_add_duplicate_process(self):
        a = AliquotType(name='aliquot_a', numeric_code='55', alpha_code='AA')
        b = AliquotType(name='aliquot_b', numeric_code='66', alpha_code='BB')
        a.add_derivatives(b)
        process = Process(aliquot_type=b, aliquot_count=3)
        processing_profile = ProcessingProfile(
            name='process', aliquot_type=a)
        processing_profile.add_processes(process)
        self.assertRaises(
            ProcessingProfileAlreadyAdded,
            processing_profile.add_processes, process)

    def test_requisition_specimen(self):
        """Asserts can create a requisition.
        """
        subject_visit = SubjectVisit.objects.create()
        SubjectRequisition.objects.create(
            subject_visit=subject_visit,
            panel=self.panel.panel_model_obj)

    def test_requisition_identifier2(self):
        """Asserts requisition identifier is set on requisition.
        """
        subject_visit = SubjectVisit.objects.create()
        requisition = SubjectRequisition.objects.create(
            subject_visit=subject_visit,
            panel=self.panel.panel_model_obj,
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
            panel=self.panel.panel_model_obj,
            is_drawn=NO,
            reason_not_drawn=NOT_APPLICABLE)
        pattern = re.compile('[0-9]{2}[A-Z0-9]{5}')
        self.assertFalse(pattern.match(requisition.requisition_identifier))

    def test_requisition_identifier5(self):
        """Asserts requisition identifier is set if specimen
        changed to drawn.
        """
        subject_visit = SubjectVisit.objects.create()
        requisition = SubjectRequisition.objects.create(
            subject_visit=subject_visit,
            panel=self.panel.panel_model_obj,
            is_drawn=NO)
        requisition.is_drawn = YES
        requisition.save()
        pattern = re.compile('[0-9]{2}[A-Z0-9]{5}')
        self.assertTrue(pattern.match(requisition.requisition_identifier))

    def test_requisition_identifier6(self):
        """Asserts requisition identifier is unchanged on save/resave.
        """
        subject_visit = SubjectVisit.objects.create()
        requisition = SubjectRequisition.objects.create(
            subject_visit=subject_visit,
            panel=self.panel.panel_model_obj,
            is_drawn=YES)
        requisition_identifier = requisition.requisition_identifier
        requisition.is_drawn = YES
        requisition.save()
        self.assertEqual(
            requisition_identifier, requisition.requisition_identifier)
