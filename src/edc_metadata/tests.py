from django.apps import apps as django_apps
from django.test import TestCase

from edc_example.factories import SubjectConsentFactory, SubjectVisitFactory, SubjectRequisitionFactory
from edc_example.models import (
    SubjectVisit, Appointment, Enrollment, CrfMetadata, RequisitionMetadata, CrfOne)
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED, UNSCHEDULED, MISSED_VISIT

from .constants import KEYED


class TestMetadata(TestCase):

    def setUp(self):
        self.app_config = django_apps.get_app_config('edc_metadata')
        edc_registration_app_config = django_apps.get_app_config('edc_registration')
        RegisteredSubject = edc_registration_app_config.model
        subject_consent = SubjectConsentFactory()
        self.registered_subject = RegisteredSubject.objects.get(
            subject_identifier=subject_consent.subject_identifier)
        enrollment = Enrollment.objects.create(subject_identifier=subject_consent.subject_identifier)
        visit_schedule = site_visit_schedules.get_visit_schedule(enrollment._meta.visit_schedule_name)
        schedule = visit_schedule.get_schedule(enrollment._meta.label_lower)
        self.first_visit = schedule.get_first_visit()
        self.first_appointment = Appointment.objects.get(
            subject_identifier=enrollment.subject_identifier,
            visit_code=self.first_visit.code)
        self.panel_name = self.first_visit.requisitions[0].panel.name

    def test_visit_creates_metadata(self):
        self.subject_visit = SubjectVisitFactory(
            appointment=self.first_appointment,
            reason=SCHEDULED)
        self.assertEqual(CrfMetadata.objects.all().count(), len(self.first_visit.crfs))
        self.assertEqual(RequisitionMetadata.objects.all().count(), len(self.first_visit.requisitions))

    def test_visit_creates_metadata2(self):
        self.subject_visit = SubjectVisitFactory(
            appointment=self.first_appointment,
            reason=UNSCHEDULED)
        self.assertEqual(CrfMetadata.objects.all().count(), len(self.first_visit.crfs))
        self.assertEqual(RequisitionMetadata.objects.all().count(), len(self.first_visit.requisitions))

    def test_visit_does_not_create_metadata_if_missed(self):
        self.subject_visit = SubjectVisitFactory(
            appointment=self.first_appointment,
            reason=MISSED_VISIT)
        self.assertEqual(CrfMetadata.objects.all().count(), 0)
        self.assertEqual(RequisitionMetadata.objects.all().count(), 0)

    def test_visit_creates_metadata_for_all_reasons(self):
        for reason in self.app_config.create_on_reasons:
            try:
                SubjectVisit.objects.get(appointment=self.first_appointment)
                self.subject_visit.reason = reason
                self.subject_visit.save()
            except SubjectVisit.DoesNotExist:
                self.subject_visit = SubjectVisitFactory(
                    appointment=self.first_appointment,
                    reason=reason)
            self.assertEqual(CrfMetadata.objects.all().count(), len(self.first_visit.crfs))
            self.assertEqual(RequisitionMetadata.objects.all().count(), len(self.first_visit.requisitions))

    def test_visit_deletes_metadata(self):
        self.subject_visit = SubjectVisitFactory(
            appointment=self.first_appointment,
            reason=SCHEDULED)
        self.assertEqual(CrfMetadata.objects.all().count(), len(self.first_visit.crfs))
        self.assertEqual(RequisitionMetadata.objects.all().count(), len(self.first_visit.requisitions))
        for reason in self.app_config.delete_on_reasons:
            self.subject_visit.reason = reason
            self.subject_visit.save()
            self.assertEqual(CrfMetadata.objects.all().count(), 0)
            self.assertEqual(RequisitionMetadata.objects.all().count(), 0)

    def test_updates_crf_metadata(self):
        self.subject_visit = SubjectVisitFactory(
            appointment=self.first_appointment,
            reason=SCHEDULED)
        self.assertEqual(CrfMetadata.objects.all().count(), len(self.first_visit.crfs))
        CrfOne.objects.create(subject_visit=self.subject_visit)
        self.assertEqual(CrfMetadata.objects.filter(entry_status=KEYED).count(), 1)

    def test_updates_crf_metadata2(self):
        self.subject_visit = SubjectVisitFactory(
            appointment=self.first_appointment,
            reason=SCHEDULED)
        self.assertEqual(CrfMetadata.objects.all().count(), len(self.first_visit.crfs))
        crf_one = CrfOne.objects.create(subject_visit=self.subject_visit)
        crf_one.save()
        self.assertEqual(CrfMetadata.objects.filter(entry_status=KEYED).count(), 1)

    def test_updates_requisition_metadata(self):
        self.subject_visit = SubjectVisitFactory(
            appointment=self.first_appointment,
            reason=SCHEDULED)
        self.assertEqual(RequisitionMetadata.objects.all().count(), len(self.first_visit.requisitions))
        SubjectRequisitionFactory(
            subject_visit=self.subject_visit,
            panel_name=self.panel_name)
        self.assertEqual(RequisitionMetadata.objects.filter(entry_status=KEYED, panel_name=self.panel_name).count(), 1)

    def test_updates_requisition_metadata2(self):
        self.subject_visit = SubjectVisitFactory(
            appointment=self.first_appointment,
            reason=SCHEDULED)
        self.assertEqual(RequisitionMetadata.objects.all().count(), len(self.first_visit.requisitions))
        subject_requisition = SubjectRequisitionFactory(
            subject_visit=self.subject_visit,
            panel_name=self.panel_name)
        subject_requisition.save()
        self.assertEqual(RequisitionMetadata.objects.filter(entry_status=KEYED, panel_name=self.panel_name).count(), 1)

    def test_resets_crf_metadata_on_delete(self):
        self.subject_visit = SubjectVisitFactory(
            appointment=self.first_appointment,
            reason=SCHEDULED)
        self.assertEqual(CrfMetadata.objects.all().count(), len(self.first_visit.crfs))
        self.assertEqual(RequisitionMetadata.objects.all().count(), len(self.first_visit.requisitions))
        crf_one = CrfOne.objects.create(subject_visit=self.subject_visit)
        crf_metadata = CrfMetadata.objects.get(
            subject_identifier=self.subject_visit.subject_identifier,
            model=crf_one._meta.label_lower,
            entry_status=KEYED)
        crf_one.delete()
        crf_metadata = CrfMetadata.objects.get(pk=crf_metadata.pk)
        self.assertNotEqual(crf_metadata.entry_status, KEYED)
        self.assertEqual(CrfMetadata.objects.all().count(), len(self.first_visit.crfs))

    def test_resets_requisition_metadata_on_delete(self):
        self.subject_visit = SubjectVisitFactory(
            appointment=self.first_appointment,
            reason=SCHEDULED)
        self.assertEqual(CrfMetadata.objects.all().count(), len(self.first_visit.crfs))
        self.assertEqual(RequisitionMetadata.objects.all().count(), len(self.first_visit.requisitions))
        subject_requisition = SubjectRequisitionFactory(
            subject_visit=self.subject_visit,
            panel_name=self.panel_name)
        metadata = RequisitionMetadata.objects.get(
            subject_identifier=self.subject_visit.subject_identifier,
            model=subject_requisition._meta.label_lower,
            entry_status=KEYED)
        subject_requisition.delete()
        metadata = RequisitionMetadata.objects.get(pk=metadata.pk)
        self.assertNotEqual(metadata.entry_status, KEYED)
        self.assertEqual(RequisitionMetadata.objects.all().count(), len(self.first_visit.requisitions))

    def test_get_metadata_for_subject_visit(self):
        """Asserts can get metadata for a subject and visit code."""
        self.subject_visit = SubjectVisitFactory(
            appointment=self.first_appointment,
            reason=SCHEDULED)
        a = []
        for metadata in self.subject_visit.metadata.values():
            for md in metadata:
                a.append(md.model)
        a.sort()
        schedule = site_visit_schedules.get_schedule(
            self.subject_visit.metadata_query_options['schedule_name'])
        b = [crf.model._meta.label_lower
             for crf in schedule.get_visit(self.subject_visit.visit_code).crfs]
        b.extend([requisition.model._meta.label_lower
                  for requisition in schedule.get_visit(self.subject_visit.visit_code).requisitions])
        b.sort()
        self.assertEqual(a, b)
