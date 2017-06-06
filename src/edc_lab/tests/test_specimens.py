from django.test import TestCase, tag

from edc_constants.constants import YES, NO

from ..lab import AliquotType, Process, ProcessingProfile
from ..lab import Specimen, SpecimenNotDrawnError
from ..models import Aliquot
from .models import SubjectRequisition, SubjectVisit
from .site_labs_test_mixin import TestMixin


@tag('specimen')
class TestSpecimen(TestMixin, TestCase):

    def setUp(self):
        self.setup_site_labs()
        self.subject_visit = SubjectVisit.objects.create(
            subject_identifier='1111111111')

    def test_specimen(self):
        requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel_name=self.panel.name,
            protocol_number='999',
            is_drawn=YES)
        Specimen(requisition=requisition)

    def test_specimen_repr(self):
        requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel_name=self.panel.name,
            protocol_number='999',
            is_drawn=YES)
        specimen = Specimen(requisition=requisition)
        self.assertTrue(repr(specimen))

    def test_specimen_from_pk(self):
        requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel_name=self.panel.name,
            protocol_number='999',
            is_drawn=YES)
        Specimen(requisition_pk=requisition.pk)

    def test_specimen_not_drawn(self):
        requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel_name=self.panel.name,
            protocol_number='999',
            is_drawn=NO)
        self.assertRaises(
            SpecimenNotDrawnError,
            Specimen, requisition=requisition)


@tag('specimen')
class TestSpecimen2(TestMixin, TestCase):

    def setUp(self):
        self.setup_site_labs()
        self.subject_visit = SubjectVisit.objects.create(
            subject_identifier='1111111111')
        self.requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel_name=self.panel.name,
            protocol_number='999',
            is_drawn=YES)
        self.specimen = Specimen(requisition=self.requisition)

    def test_requisition_creates_aliquot(self):
        """Asserts passing requisition to specimen class
        creates an aliquot.
        """
        requisition = SubjectRequisition.objects.get(pk=self.requisition.pk)
        self.assertEqual(
            Aliquot.objects.filter(
                requisition_identifier=requisition.requisition_identifier,
                is_primary=True).count(), 1)

    def test_requisition_gets_aliquot(self):
        """Asserts passing requisition to specimen class gets
        an existing aliquot.
        """
        # instantiate again, to get primary aliquot
        specimen = Specimen(requisition=self.requisition)
        obj = Aliquot.objects.get(
            requisition_identifier=self.requisition.requisition_identifier,
            is_primary=True)
        self.assertEqual(
            specimen.aliquots[0].aliquot_identifier, obj.aliquot_identifier)

    def test_process_repr(self):
        a = AliquotType(name='aliquot_a', numeric_code='55', alpha_code='AA')
        process = Process(aliquot_type=a)
        self.assertTrue(repr(process))

    def test_process_profile_repr(self):
        a = AliquotType(name='aliquot_a', numeric_code='55', alpha_code='AA')
        processing_profile = ProcessingProfile(
            name='processing_profile', aliquot_type=a)
        self.assertTrue(repr(processing_profile))

    def test_specimen_process(self):
        """Asserts calling process creates the correct number
        of child aliquots.
        """
        self.assertEqual(self.specimen.aliquots.count(), 1)
        self.specimen.process()
        self.assertEqual(self.specimen.aliquots.count(),
                         self.profile_aliquot_count + 1)

    def test_specimen_process2(self):
        """Asserts calling process more than once has no effect.
        """
        self.specimen.process()
        self.assertEqual(self.specimen.aliquots.count(),
                         self.profile_aliquot_count + 1)
        self.specimen.process()
        self.specimen.process()
        self.assertEqual(self.specimen.aliquots.count(),
                         self.profile_aliquot_count + 1)

    def test_specimen_process_identifier_prefix(self):
        """Assert all aliquots start with the correct identifier
        prefix.
        """
        self.specimen.process()
        for aliquot in self.specimen.aliquots.order_by('created'):
            self.assertIn(
                self.specimen.primary_aliquot.identifier_prefix,
                aliquot.aliquot_identifier)

    def test_specimen_process_identifier_parent_segment(self):
        """Assert all aliquots have correct 4 chars parent_segment.
        """
        self.specimen.process()
        parent_segment = self.specimen.primary_aliquot.aliquot_identifier[-4:]

        aliquot = self.specimen.aliquots.order_by('count')[0]
        self.assertTrue(aliquot.is_primary)
        self.assertEqual('0000', aliquot.aliquot_identifier[-8:-4])

        for aliquot in self.specimen.aliquots.order_by('count')[1:]:
            self.assertFalse(aliquot.is_primary)
            self.assertEqual(parent_segment, aliquot.aliquot_identifier[-8:-4])

    def test_specimen_process_identifier_child_segment(self):
        """Assert all aliquots have correct 4 chars child_segment.
        """
        self.specimen.process()

        aliquot = self.specimen.aliquots.order_by('count')[0]
        self.assertTrue(aliquot.is_primary)
        self.assertEqual('5501', aliquot.aliquot_identifier[-4:])

        for index, aliquot in enumerate(self.specimen.aliquots.order_by('count')[1:]):
            index += 2
            self.assertFalse(aliquot.is_primary)
            self.assertEqual(f'66{str(index).zfill(2)}', aliquot.aliquot_identifier[-4:])
