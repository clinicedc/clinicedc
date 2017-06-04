from django.test import TestCase, tag

from edc_constants.constants import YES, NO

from ..lab import AliquotType, RequisitionPanel, Process, ProcessingProfile, LabProfile
from ..lab import Specimen, SpecimenNotDrawnError
from ..site_labs import site_labs
from .models import SubjectRequisition, SubjectVisit


@tag('specimen')
class TestSpecimen(TestCase):

    def setUp(self):
        self.setup_site_labs()
        self.subject_visit = SubjectVisit.objects.create(
            subject_identifier='1111111111')
        self.requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel_name=self.panel.name,
            protocol_number='999',
            is_drawn=YES)

    def setup_site_labs(self):
        site_labs._registry = {}
        site_labs.loaded = False

        # create aliquots and their relationship
        a = AliquotType(name='aliquot_a', numeric_code='55', alpha_code='AA')
        b = AliquotType(name='aliquot_b', numeric_code='66', alpha_code='BB')
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

    def test_specimen(self):
        Specimen(
            requisition=self.requisition)

    def test_specimen_from_pk(self):
        self.requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel_name=self.panel.name,
            protocol_number='999',
            is_drawn=YES)
        Specimen(requisition_pk=self.requisition.pk)

    def test_specimen_not_drawn(self):
        self.requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel_name=self.panel.name,
            protocol_number='999',
            is_drawn=NO)
        self.assertRaises(
            SpecimenNotDrawnError,
            Specimen, requisition=self.requisition)
