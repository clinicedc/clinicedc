from django.apps import apps as django_apps
from django.test import TestCase, tag

from edc_constants.constants import YES

from ..models import Aliquot
from ..lab import AliquotType, Specimen, Process, ProcessingProfile, LabProfile, RequisitionPanel
from ..site_labs import site_labs
from .models import SubjectVisit, SubjectRequisition

app_config = django_apps.get_app_config('edc_lab')


class LabTests(TestCase):

    def setUp(self):
        lab_profile = LabProfile(
            name='lab_profile', requisition_model=SubjectRequisition)
        a = AliquotType(name='aliquot_a')
        b = AliquotType(name='aliquot_b')
        a.add_derivatives(b)
        process = Process(aliquot_type=a, aliquot_count=3)
        processing_profile = ProcessingProfile(
            name='process', aliquot_type=a)
        processing_profile.add_processes(process)
        panel = RequisitionPanel(
            name='panel', model=SubjectRequisition,
            aliquot_type=a)
        lab_profile.add_panel(panel)
        site_labs.register(lab_profile)

        self.subject_identifier = '111111111'
        self.subject_visit = SubjectVisit.objects.create(
            subject_identifier=self.subject_identifier)
        self.panel_name = 'my_panel'

    def test_requisition_creates_aliquot(self):
        """Asserts passing requisition to specimen class creates an aliquot."""
        requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel_name=self.panel_name,
            is_drawn=YES)
        Specimen(requisition)
        self.assertIsNotNone(requisition.specimen_identifier)
        self.assertEqual(Aliquot.objects.filter(
            specimen_identifier=requisition.specimen_identifier).count(), 1)

    def test_requisition_creates_primary_aliquot(self):
        """Asserts passing requisition to specimen class creates an aliquot that is the primary."""
        requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel_name=self.panel_name,
            is_drawn=YES)
        specimen = Specimen(requisition)
        self.assertIsNotNone(specimen.requisition.specimen_identifier)
        self.assertEqual(Aliquot.objects.filter(
            specimen_identifier=specimen.requisition.specimen_identifier,
            is_primary=True).count(), 1)
        self.assertTrue(SubjectRequisition.objects.get(
            specimen_identifier=specimen.requisition.specimen_identifier))

    def test_requisition_creates_primary_aliquot_only_once(self):
        """Asserts passing the same requisition to specimen class does not recreate a primary aliquot."""
        requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel_name=self.panel_name,
            is_drawn=YES)
        Specimen(requisition)
        self.assertIsNotNone(requisition.specimen_identifier)
        self.assertEqual(Aliquot.objects.filter(
            specimen_identifier=requisition.specimen_identifier,
            is_primary=True).count(), 1)
        Specimen(requisition)
        self.assertEqual(Aliquot.objects.filter(
            specimen_identifier=requisition.specimen_identifier,
            is_primary=True).count(), 1)

    def test_requisition_gets_primary_aliquot_and_aliquots(self):
        """Asserts specimen class knows the primary aliquot and all aliquots of this specimen."""
        requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel_name=self.panel_name,
            is_drawn=YES)
        specimen = Specimen(requisition)
        self.assertIsNotNone(specimen.primary_aliquot)
        self.assertEqual(specimen.aliquot_count, 1)

    def test_requisition_create_aliquots(self):
        """Asserts aliquot class can create child aliquots from itself.
        """
        requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel_name=self.panel_name,
            is_drawn=YES)
        specimen = Specimen(requisition)
        specimen.primary_aliquot.create_aliquots('36', 3)
        self.assertEqual(specimen.aliquot_count, 4)
        self.assertEqual(
            app_config.aliquot_model.objects.filter(aliquot_type='36').count(), 3)

    def test_requisition_create_aliquots_check_identifier(self):
        """Asserts aliquot class can create child aliquots from
        itself with the correct identifier format.
        """
        requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel_name=self.panel_name,
            is_drawn=YES)
        specimen = Specimen(requisition)
        specimen.primary_aliquot.create_aliquots('36', 3)
        self.assertEqual(specimen.aliquot_count, 4)
        self.assertEqual(app_config.aliquot_model.objects.filter(
            aliquot_identifier__startswith=specimen.primary_aliquot.aliquot_identifier[0:10]).count(), 4)
        self.assertEqual(app_config.aliquot_model.objects.filter(
            aliquot_identifier__endswith=specimen.primary_aliquot.aliquot_identifier[-4:]).count(), 1)
        self.assertEqual(app_config.aliquot_model.objects.filter(
            aliquot_identifier__startswith=specimen.primary_aliquot.aliquot_identifier[0:14]).count(), 1)

    def test_aliquots_identifier_sequence(self):
        """Asserts aliquot class can create child aliquots from
        itself with the correct sequence numbers.
        """
        requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel_name=self.panel_name,
            is_drawn=YES)
        specimen = Specimen(requisition)
        specimen.primary_aliquot.create_aliquots('36', 3)
        for index, obj in enumerate(app_config.aliquot_model.objects.filter(is_primary=False).order_by('count')):
            self.assertEqual(obj.aliquot_identifier[-1:], str(index + 1))

    def test_aliquots_identifier_sequence2(self):
        """Asserts aliquot class can create child aliquots from
        itself with the correct sequence numbers even if multiple
        specimens are processed.
        """
        requisition1 = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel_name=self.panel_name,
            is_drawn=YES)
        requisition2 = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel_name=self.first_visit.requisitions[1].panel.name,
            is_drawn=YES)
        specimen1 = Specimen(requisition1)
        specimen1.primary_aliquot.create_aliquots('36', 3)
        specimen2 = Specimen(requisition2)
        specimen2.primary_aliquot.create_aliquots('11', 5)
        for index, obj in enumerate(app_config.aliquot_model.objects.filter(
                parent_identifier=specimen1.primary_aliquot.aliquot_identifier,
                is_primary=False).order_by('count')):
            self.assertEqual(obj.aliquot_identifier[-1:], str(index + 1))
            self.assertEqual(obj.aliquot_identifier[-4:-2], '36')
        for index, obj in enumerate(app_config.aliquot_model.objects.filter(
                parent_identifier=specimen2.primary_aliquot.aliquot_identifier,
                is_primary=False).order_by('count')):
            self.assertEqual(obj.aliquot_identifier[-1:], str(index + 1))
            self.assertEqual(obj.aliquot_identifier[-4:-2], '11')

    def test_create_aliquots_by_profile(self):
        requisition1 = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel_name=self.panel_name,
            is_drawn=YES)
        specimen1 = Specimen(requisition1)
        specimen1.primary_aliquot.create_aliquots_by_processing_profile(
            requisition1.panel_name, requisition1._meta.label_lower)
        alpha_codes = []
        for aliquot in app_config.aliquot_model.objects.filter(
                parent_identifier=specimen1.primary_aliquot.aliquot_identifier,
                is_primary=False).order_by('aliquot_identifier'):
            alpha_codes.append(aliquot.aliquot_identifier[-4:-2])
        alpha_codes.sort()
        self.assertEqual(
            alpha_codes, ['12', '12', '12', '36', '36', '36', '36'])
