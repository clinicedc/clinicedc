import re

from django.apps import apps as django_apps
from django.test import TestCase

from edc_example.factories import SubjectConsentFactory, EnrollmentFactory, SubjectVisitFactory, SubjectRequisitionFactory
from edc_example.models import Appointment, SubjectRequisition, Aliquot
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from django.utils import timezone
from edc_lab.requisition.identifier import Identifier
from edc_constants.constants import YES, NO
from edc_lab.collection.specimen import Specimen

app_config = django_apps.get_app_config('edc_lab')


class LabTests(TestCase):

    def setUp(self):
        subject_consent = SubjectConsentFactory()
        enrollment = EnrollmentFactory(subject_identifier=subject_consent.subject_identifier)
        visit_schedule = site_visit_schedules.get_visit_schedule(enrollment._meta.visit_schedule_name)
        self.schedule = visit_schedule.get_schedule(enrollment._meta.label_lower)
        self.first_visit = self.schedule.get_first_visit()
        first_appointment = Appointment.objects.get(
            subject_identifier=enrollment.subject_identifier,
            visit_code=self.first_visit.code)
        self.subject_visit = SubjectVisitFactory(appointment=first_appointment)
        self.panel_name = self.first_visit.requisitions[0].panel.name

    def test_requisition_specimen(self):
        """Asserts can create a requisition."""
        self.assertTrue(
            SubjectRequisitionFactory(
                subject_visit=self.subject_visit,
                panel_name=self.panel_name,
                requisition_datetime=timezone.now()))

    def test_requisition_identifier(self):
        """Asserts requisition identifier class creates identifier with correct format."""
        identifier = Identifier(SubjectRequisition)
        pattern = re.compile('[0-9]{2}[A-Z0-9]{5}')
        self.assertTrue(pattern.match(str(identifier)))

    def test_requisition_identifier2(self):
        """Asserts requisition identifier is set on requisition."""
        requisition = SubjectRequisitionFactory(
            subject_visit=self.subject_visit,
            panel_name=self.panel_name,
            requisition_datetime=timezone.now(),
            is_drawn=YES)
        pattern = re.compile('[0-9]{2}[A-Z0-9]{5}')
        self.assertTrue(pattern.match(requisition.requisition_identifier))

    def test_requisition_identifier3(self):
        """Asserts requisition identifier is NOT set on requisition if specimen not drawn."""
        requisition = SubjectRequisitionFactory(
            subject_visit=self.subject_visit,
            panel_name=self.panel_name,
            requisition_datetime=timezone.now(),
            is_drawn=NO)
        pattern = re.compile('[0-9]{2}[A-Z0-9]{5}')
        self.assertFalse(pattern.match(requisition.requisition_identifier))

    def test_requisition_identifier4(self):
        """Asserts requisition identifier is CLEARED if specimen changed to not drawn."""
        requisition = SubjectRequisitionFactory(
            subject_visit=self.subject_visit,
            panel_name=self.panel_name,
            requisition_datetime=timezone.now(),
            is_drawn=YES)
        requisition.is_drawn = NO
        requisition.save()
        pattern = re.compile('[0-9]{2}[A-Z0-9]{5}')
        self.assertFalse(pattern.match(requisition.requisition_identifier))

    def test_requisition_identifier5(self):
        """Asserts requisition identifier is set if specimen changed to drawn."""
        requisition = SubjectRequisitionFactory(
            subject_visit=self.subject_visit,
            panel_name=self.panel_name,
            requisition_datetime=timezone.now(),
            is_drawn=NO)
        requisition.is_drawn = YES
        requisition.save()
        pattern = re.compile('[0-9]{2}[A-Z0-9]{5}')
        self.assertTrue(pattern.match(requisition.requisition_identifier))

    def test_requisition_identifier6(self):
        """Asserts requisition identifier is unchanged on save/resave."""
        requisition = SubjectRequisitionFactory(
            subject_visit=self.subject_visit,
            panel_name=self.panel_name,
            requisition_datetime=timezone.now(),
            is_drawn=YES)
        requisition_identifier = requisition.requisition_identifier
        requisition.is_drawn = YES
        requisition.save()
        self.assertEqual(requisition_identifier, requisition.requisition_identifier)

    def test_requisition_creates_aliquot(self):
        """Asserts passing requisition to specimen class creates an aliquot."""
        requisition = SubjectRequisitionFactory(
            subject_visit=self.subject_visit,
            panel_name=self.panel_name,
            requisition_datetime=timezone.now(),
            is_drawn=YES)
        Specimen(requisition)
        self.assertIsNotNone(requisition.specimen_identifier)
        self.assertEqual(Aliquot.objects.filter(specimen_identifier=requisition.specimen_identifier).count(), 1)

    def test_requisition_creates_primary_aliquot(self):
        """Asserts passing requisition to specimen class creates an aliquot that is the primary."""
        requisition = SubjectRequisitionFactory(
            subject_visit=self.subject_visit,
            panel_name=self.panel_name,
            requisition_datetime=timezone.now(),
            is_drawn=YES)
        Specimen(requisition)
        self.assertIsNotNone(requisition.specimen_identifier)
        self.assertEqual(Aliquot.objects.filter(
            specimen_identifier=requisition.specimen_identifier,
            is_primary=True).count(), 1)

    def test_requisition_creates_primary_aliquot_only_once(self):
        """Asserts passing the same requisition to specimen class does not recreate a primary aliquot."""
        requisition = SubjectRequisitionFactory(
            subject_visit=self.subject_visit,
            panel_name=self.panel_name,
            requisition_datetime=timezone.now(),
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
        requisition = SubjectRequisitionFactory(
            subject_visit=self.subject_visit,
            panel_name=self.panel_name,
            requisition_datetime=timezone.now(),
            is_drawn=YES)
        specimen = Specimen(requisition)
        self.assertIsNotNone(specimen.primary_aliquot)
        self.assertEqual(specimen.aliquot_count, 1)

    def test_requisition_create_aliquots(self):
        """Asserts aliquot class can create child aliquots from itself."""
        requisition = SubjectRequisitionFactory(
            subject_visit=self.subject_visit,
            panel_name=self.panel_name,
            requisition_datetime=timezone.now(),
            is_drawn=YES)
        specimen = Specimen(requisition)
        specimen.primary_aliquot.create_aliquots('36', 3)
        self.assertEqual(specimen.aliquot_count, 4)
        self.assertEqual(app_config.aliquot_model.objects.filter(aliquot_type='36').count(), 3)

    def test_requisition_create_aliquots_check_identifier(self):
        """Asserts aliquot class can create child aliquots from itself with the correct identifier format."""
        requisition = SubjectRequisitionFactory(
            subject_visit=self.subject_visit,
            panel_name=self.panel_name,
            requisition_datetime=timezone.now(),
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
        """Asserts aliquot class can create child aliquots from itself with the correct sequence numbers."""
        requisition = SubjectRequisitionFactory(
            subject_visit=self.subject_visit,
            panel_name=self.panel_name,
            requisition_datetime=timezone.now(),
            is_drawn=YES)
        specimen = Specimen(requisition)
        specimen.primary_aliquot.create_aliquots('36', 3)
        for index, obj in enumerate(app_config.aliquot_model.objects.filter(is_primary=False).order_by('count')):
            self.assertEqual(obj.aliquot_identifier[-1:], str(index + 1))

    def test_aliquots_identifier_sequence2(self):
        """Asserts aliquot class can create child aliquots from itself with the correct sequence numbers
        even if multiple specimens are processed."""
        requisition1 = SubjectRequisitionFactory(
            subject_visit=self.subject_visit,
            panel_name=self.panel_name,
            requisition_datetime=timezone.now(),
            is_drawn=YES)
        requisition2 = SubjectRequisitionFactory(
            subject_visit=self.subject_visit,
            panel_name=self.first_visit.requisitions[1].panel.name,
            requisition_datetime=timezone.now(),
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
        requisition1 = SubjectRequisitionFactory(
            subject_visit=self.subject_visit,
            panel_name=self.panel_name,
            requisition_datetime=timezone.now(),
            is_drawn=YES)
        specimen1 = Specimen(requisition1)
        specimen1.primary_aliquot.create_aliquots_by_processing_profile('viral_load')
        alpha_codes = []
        for aliquot in app_config.aliquot_model.objects.filter(
                parent_identifier=specimen1.primary_aliquot.aliquot_identifier,
                is_primary=False).order_by('aliquot_identifier'):
            alpha_codes.append(aliquot.aliquot_identifier[-4:-2])
        alpha_codes.sort()
        self.assertEqual(alpha_codes, ['12', '12', '12', '36', '36', '36', '36'])

    def test_collection(self):
        requisition1 = SubjectRequisitionFactory(
            subject_visit=self.subject_visit,
            panel_name=self.first_visit.requisitions[0].panel.name,
            requisition_datetime=timezone.now(),
            is_drawn=YES)
        requisition2 = SubjectRequisitionFactory(
            subject_visit=self.subject_visit,
            panel_name=self.first_visit.requisitions[1].panel.name,
            requisition_datetime=timezone.now(),
            is_drawn=YES)
        collection = Collection()
        collection.add(requisition1.requisition_identifier)
        collection.add(requisition2.requisition_identifier)
        self.assertEqual(len(collection.specimens), 2)
        self.assertIn(requisition1.requisition_identifier, [s.requisition_identifier for s in collection.specimens])
        self.assertIn(requisition2.requisition_identifier, [s.requisition_identifier for s in collection.specimens])
        self.assertEqual(
            app_config.aliquot_model.objects.filter(
                specimen_identifier__in=[s.specimen_identifier for s in collection.specimens]), 2)
        
#         requisition = SubjectRequisition.objects.get(requisition_identifier=requisition.requisition_identifier)
#         aliquot = Aliquot.objects.get()

    def test_process_aliquot(self):
        pass
