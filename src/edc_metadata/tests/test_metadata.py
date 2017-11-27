from django.test import TestCase, tag
from edc_appointment.models import Appointment
from edc_metadata.metadata_updater import MetadataUpdater
from edc_reference import site_reference_configs
from edc_registration.models import RegisteredSubject
from edc_visit_schedule import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED, UNSCHEDULED, MISSED_VISIT

from ..constants import KEYED, REQUIRED
from ..metadata import CreatesMetadataError
from ..models import CrfMetadata, RequisitionMetadata
from .models import SubjectVisit, Enrollment, CrfOne, CrfTwo, CrfThree, SubjectRequisition
from .reference_configs import register_to_site_reference_configs
from .visit_schedule import visit_schedule


class TestCreatesDeletesMetadata(TestCase):

    def setUp(self):
        register_to_site_reference_configs()
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)
        site_reference_configs.register_from_visit_schedule(
            site_visit_schedules, autodiscover=False)
        self.schedule = site_visit_schedules.get_schedule(
            visit_schedule_name='visit_schedule',
            schedule_name='schedule')
        self.subject_identifier = '1111111'
        RegisteredSubject.objects.create(
            subject_identifier=self.subject_identifier)
        self.assertEqual(CrfMetadata.objects.all().count(), 0)
        self.assertEqual(RequisitionMetadata.objects.all().count(), 0)
        Enrollment.objects.create(
            subject_identifier=self.subject_identifier,
            facility_name='7-day-clinic')
        self.appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code=self.schedule.visits.first.code)

    def test_metadata_updater_repr(self):
        obj = MetadataUpdater()
        self.assertTrue(repr(obj))

    def test_creates_metadata_on_scheduled(self):
        SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED)
        self.assertGreater(CrfMetadata.objects.all().count(), 0)
        self.assertGreater(RequisitionMetadata.objects.all().count(), 0)

    def test_creates_metadata_on_unscheduled(self):
        SubjectVisit.objects.create(
            appointment=self.appointment, reason=UNSCHEDULED)
        self.assertGreater(CrfMetadata.objects.all().count(), 0)
        self.assertGreater(RequisitionMetadata.objects.all().count(), 0)

    def test_does_not_creates_metadata_on_missed(self):
        SubjectVisit.objects.create(
            appointment=self.appointment, reason=MISSED_VISIT)
        self.assertEqual(CrfMetadata.objects.all().count(), 0)
        self.assertEqual(RequisitionMetadata.objects.all().count(), 0)

    def test_unknown_reason_raises(self):
        self.assertRaises(
            CreatesMetadataError,
            SubjectVisit.objects.create,
            appointment=self.appointment, reason='ERIK')

    def test_change_to_unknown_reason_raises(self):
        obj = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED)
        obj.reason = 'ERIK'
        self.assertRaises(CreatesMetadataError, obj.save)

    def test_deletes_metadata_on_changed_reason(self):
        obj = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED)
        obj.reason = MISSED_VISIT
        obj.save()
        self.assertEqual(CrfMetadata.objects.all().count(), 0)
        self.assertEqual(RequisitionMetadata.objects.all().count(), 0)


class TestUpdatesMetadata(TestCase):

    def setUp(self):
        register_to_site_reference_configs()
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)
        site_reference_configs.register_from_visit_schedule(
            site_visit_schedules, autodiscover=False)
        self.schedule = site_visit_schedules.get_schedule(
            visit_schedule_name='visit_schedule',
            schedule_name='schedule')
        self.subject_identifier = '1111111'
        RegisteredSubject.objects.create(
            subject_identifier=self.subject_identifier)
        self.assertEqual(CrfMetadata.objects.all().count(), 0)
        self.assertEqual(RequisitionMetadata.objects.all().count(), 0)
        Enrollment.objects.create(
            subject_identifier=self.subject_identifier,
            facility_name='7-day-clinic')
        self.appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code=self.schedule.visits.first.code)

    def test_updates_crf_metadata_as_keyed(self):
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED)
        CrfOne.objects.create(subject_visit=subject_visit)
        self.assertEqual(CrfMetadata.objects.filter(
            entry_status=KEYED,
            model='edc_metadata.crfone',
            visit_code=subject_visit.visit_code).count(), 1)
        self.assertEqual(CrfMetadata.objects.filter(
            entry_status=REQUIRED,
            model='edc_metadata.crftwo',
            visit_code=subject_visit.visit_code).count(), 1)
        self.assertEqual(CrfMetadata.objects.filter(
            entry_status=REQUIRED,
            model='edc_metadata.crfthree',
            visit_code=subject_visit.visit_code).count(), 1)

    def test_updates_all_crf_metadata_as_keyed(self):
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED)
        CrfOne.objects.create(subject_visit=subject_visit)
        CrfTwo.objects.create(subject_visit=subject_visit)
        CrfThree.objects.create(subject_visit=subject_visit)
        for model_name in ['crfone', 'crftwo', 'crfthree']:
            self.assertEqual(CrfMetadata.objects.filter(
                entry_status=KEYED,
                model=f'edc_metadata.{model_name}',
                visit_code=subject_visit.visit_code).count(), 1)

    @tag('1')
    def test_updates_requisition_metadata_as_keyed(self):
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED)
        SubjectRequisition.objects.create(
            subject_visit=subject_visit,
            panel_name='one')
        self.assertEqual(RequisitionMetadata.objects.filter(
            entry_status=KEYED,
            model='edc_metadata.subjectrequisition',
            panel_name='one',
            visit_code=subject_visit.visit_code).count(), 1)
        self.assertEqual(RequisitionMetadata.objects.filter(
            entry_status=REQUIRED,
            model='edc_metadata.subjectrequisition',
            panel_name='two',
            visit_code=subject_visit.visit_code).count(), 1)

    def test_resets_crf_metadata_on_delete(self):
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED)
        crf_one = CrfOne.objects.create(subject_visit=subject_visit)
        crf_one.delete()
        self.assertEqual(CrfMetadata.objects.filter(
            entry_status=REQUIRED,
            model='edc_metadata.crfone',
            visit_code=subject_visit.visit_code).count(), 1)
        self.assertEqual(CrfMetadata.objects.filter(
            entry_status=REQUIRED,
            model='edc_metadata.crftwo',
            visit_code=subject_visit.visit_code).count(), 1)
        self.assertEqual(CrfMetadata.objects.filter(
            entry_status=REQUIRED,
            model='edc_metadata.crfthree',
            visit_code=subject_visit.visit_code).count(), 1)

    def test_resets_requisition_metadata_on_delete1(self):
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED)
        obj = SubjectRequisition.objects.create(
            subject_visit=subject_visit,
            panel_name='one')
        obj.delete()
        self.assertEqual(RequisitionMetadata.objects.filter(
            entry_status=REQUIRED,
            model='edc_metadata.subjectrequisition',
            panel_name='one',
            visit_code=subject_visit.visit_code).count(), 1)
        self.assertEqual(RequisitionMetadata.objects.filter(
            entry_status=REQUIRED,
            model='edc_metadata.subjectrequisition',
            panel_name='two',
            visit_code=subject_visit.visit_code).count(), 1)

    def test_resets_requisition_metadata_on_delete2(self):
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED)
        obj = SubjectRequisition.objects.create(
            subject_visit=subject_visit,
            panel_name='two')
        obj.delete()
        self.assertEqual(RequisitionMetadata.objects.filter(
            entry_status=REQUIRED,
            model='edc_metadata.subjectrequisition',
            panel_name='one',
            visit_code=subject_visit.visit_code).count(), 1)
        self.assertEqual(RequisitionMetadata.objects.filter(
            entry_status=REQUIRED,
            model='edc_metadata.subjectrequisition',
            panel_name='two',
            visit_code=subject_visit.visit_code).count(), 1)

    def test_get_metadata_for_subject_visit(self):
        """Asserts can get metadata for a subject and visit code.
        """
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED)
        a = []
        for metadata in subject_visit.metadata.values():
            for md in metadata:
                a.append(md.model)
        a.sort()
        schedule = site_visit_schedules.get_schedule(
            schedule_name=subject_visit.metadata_query_options['schedule_name'])
        b = [crf.model for crf in schedule.visits.get(
            subject_visit.visit_code).crfs]
        b.extend([
            requisition.model
            for requisition in schedule.visits.get(subject_visit.visit_code).requisitions])
        b.sort()
        self.assertEqual(a, b)
