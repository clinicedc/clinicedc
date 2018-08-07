from django.test import TestCase, tag
from edc_appointment.models import Appointment
from edc_base import get_utcnow
from edc_facility.import_holidays import import_holidays
from edc_lab.models.panel import Panel
from edc_metadata.metadata_updater import MetadataUpdater
from edc_reference import site_reference_configs
from edc_visit_schedule import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED, UNSCHEDULED, MISSED_VISIT

from ..constants import KEYED, REQUIRED
from ..metadata import CreatesMetadataError
from ..metadata import DeleteMetadataError
from ..models import CrfMetadata, RequisitionMetadata
from .models import SubjectVisit, SubjectConsent, CrfOne, CrfTwo, CrfThree, SubjectRequisition
from .reference_configs import register_to_site_reference_configs
from .visit_schedule import visit_schedule


class TestCreatesDeletesMetadata(TestCase):

    def setUp(self):
        import_holidays()
        register_to_site_reference_configs()
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)
        site_reference_configs.register_from_visit_schedule(
            visit_models={
                'edc_appointment.appointment': 'edc_metadata.subjectvisit'})
        self.subject_identifier = '1111111'
        self.assertEqual(CrfMetadata.objects.all().count(), 0)
        self.assertEqual(RequisitionMetadata.objects.all().count(), 0)
        subject_consent = SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow())
        _, self.schedule = site_visit_schedules.get_by_onschedule_model(
            'edc_metadata.onschedule')
        self.schedule.put_on_schedule(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime)
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
        self.assertGreater(CrfMetadata.objects.all().count(), 0)
        self.assertGreater(RequisitionMetadata.objects.all().count(), 0)
        obj.reason = MISSED_VISIT
        obj.save()
        self.assertEqual(CrfMetadata.objects.all().count(), 0)
        self.assertEqual(RequisitionMetadata.objects.all().count(), 0)

    def test_deletes_metadata_on_delete_visit(self):
        obj = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED)
        self.assertGreater(CrfMetadata.objects.all().count(), 0)
        self.assertGreater(RequisitionMetadata.objects.all().count(), 0)
        obj.delete()
        self.assertEqual(CrfMetadata.objects.all().count(), 0)
        self.assertEqual(RequisitionMetadata.objects.all().count(), 0)

    def test_raises_metadata_on_delete_visit_for_keyed_crf(self):
        obj = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED)
        self.assertGreater(CrfMetadata.objects.all().count(), 0)
        CrfMetadata.objects.all().update(entry_status=KEYED)
        self.assertRaises(
            DeleteMetadataError,
            obj.delete)

    def test_raises_metadata_on_delete_visit_for_keyed_requisition(self):
        obj = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED)
        self.assertGreater(RequisitionMetadata.objects.all().count(), 0)
        RequisitionMetadata.objects.all().update(entry_status=KEYED)
        self.assertRaises(
            DeleteMetadataError,
            obj.delete)


class TestUpdatesMetadata(TestCase):

    def setUp(self):
        self.panel_one = Panel.objects.create(name='one')
        self.panel_two = Panel.objects.create(name='two')
        import_holidays()
        register_to_site_reference_configs()
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)
        site_reference_configs.register_from_visit_schedule(
            visit_models={
                'edc_appointment.appointment': 'edc_metadata.subjectvisit'})
        self.subject_identifier = '1111111'
        self.assertEqual(CrfMetadata.objects.all().count(), 0)
        self.assertEqual(RequisitionMetadata.objects.all().count(), 0)
        subject_consent = SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow())
        _, self.schedule = site_visit_schedules.get_by_onschedule_model(
            'edc_metadata.onschedule')
        self.schedule.put_on_schedule(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime)
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

    def test_updates_requisition_metadata_as_keyed(self):
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED)
        SubjectRequisition.objects.create(
            subject_visit=subject_visit,
            panel=self.panel_one)
        self.assertEqual(RequisitionMetadata.objects.filter(
            entry_status=KEYED,
            model='edc_metadata.subjectrequisition',
            panel_name=self.panel_one.name,
            visit_code=subject_visit.visit_code).count(), 1)
        self.assertEqual(RequisitionMetadata.objects.filter(
            entry_status=REQUIRED,
            model='edc_metadata.subjectrequisition',
            panel_name=self.panel_two.name,
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
            panel=self.panel_one)
        obj.delete()
        self.assertEqual(RequisitionMetadata.objects.filter(
            entry_status=REQUIRED,
            model='edc_metadata.subjectrequisition',
            panel_name=self.panel_one.name,
            visit_code=subject_visit.visit_code).count(), 1)
        self.assertEqual(RequisitionMetadata.objects.filter(
            entry_status=REQUIRED,
            model='edc_metadata.subjectrequisition',
            panel_name=self.panel_two.name,
            visit_code=subject_visit.visit_code).count(), 1)

    def test_resets_requisition_metadata_on_delete2(self):
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED)
        obj = SubjectRequisition.objects.create(
            subject_visit=subject_visit,
            panel=self.panel_two)
        obj.delete()
        self.assertEqual(RequisitionMetadata.objects.filter(
            entry_status=REQUIRED,
            model='edc_metadata.subjectrequisition',
            panel_name=self.panel_one.name,
            visit_code=subject_visit.visit_code).count(), 1)
        self.assertEqual(RequisitionMetadata.objects.filter(
            entry_status=REQUIRED,
            model='edc_metadata.subjectrequisition',
            panel_name=self.panel_two.name,
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
        b = [crf.model for crf in subject_visit.schedule.visits.get(
            subject_visit.visit_code).crfs]
        b.extend([
            requisition.model
            for requisition in subject_visit.schedule.visits.get(
                subject_visit.visit_code).requisitions])
        b.sort()
        self.assertEqual(a, b)
