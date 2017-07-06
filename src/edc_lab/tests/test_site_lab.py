import re

from django.test import TestCase, tag

from edc_constants.constants import YES, NO, NOT_APPLICABLE

from ..lab import AliquotType, LabProfile, ProcessingProfile
from ..lab import Process, ProcessingProfileAlreadyAdded
from ..site_labs import SiteLabs, site_labs
from .models import SubjectRequisition, SubjectVisit
from edc_lab.tests.test_specimens import TestMixin


@tag('site')
class TestSiteLab(TestCase):

    def test_site_labs(self):
        site_lab = SiteLabs()
        self.assertFalse(site_lab.loaded)

    def test_site_labs_register(self):
        lab_profile = LabProfile(name='lab_profile')
        site_lab = SiteLabs()
        site_lab.register(lab_profile, requisition_model=SubjectRequisition)
        self.assertTrue(site_lab.loaded)

    def test_site_labs_register_none(self):
        site_lab = SiteLabs()
        site_lab.register(None)
        self.assertFalse(site_lab.loaded)


@tag('site')
class TestSiteLab2(TestMixin, TestCase):

    def setUp(self):
        self.setup_site_labs()

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
            is_drawn=NO,
            reason_not_drawn=NOT_APPLICABLE)
        pattern = re.compile('[0-9]{2}[A-Z0-9]{5}')
        self.assertFalse(pattern.match(requisition.requisition_identifier))

#     def test_requisition_identifier4(self):
#         """Asserts requisition identifier is CLEARED if specimen
#         changed to not drawn."""
#         subject_visit = SubjectVisit.objects.create()
#         requisition = SubjectRequisition.objects.create(
#             subject_visit=subject_visit,
#             panel_name=self.panel.name,
#             is_drawn=YES)
#         requisition.is_drawn = NO
#         requisition.save()
#         pattern = re.compile('[0-9]{2}[A-Z0-9]{5}')
#         self.assertFalse(pattern.match(requisition.requisition_identifier))

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
