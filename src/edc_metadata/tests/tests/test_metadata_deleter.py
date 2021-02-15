from django.test import TestCase
from edc_appointment.models import Appointment
from edc_visit_tracking.constants import MISSED_VISIT, SCHEDULED

from ...constants import KEYED
from ...metadata import DeleteMetadataError
from ...models import CrfMetadata, RequisitionMetadata
from ..models import SubjectVisit
from .metadata_test_mixin import TestMetadataMixin


class TestDeletesMetadata(TestMetadataMixin, TestCase):
    def test_deletes_metadata_on_changed_reason_toggled(self):
        SubjectVisit.objects.create(appointment=self.appointment, reason=SCHEDULED)
        appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code="2000",
        )
        obj = SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)
        self.assertEqual(CrfMetadata.objects.filter(visit_code="2000").count(), 3)
        self.assertEqual(
            RequisitionMetadata.objects.filter(visit_code="2000").count(),
            6,
        )
        obj.reason = MISSED_VISIT
        obj.save()
        self.assertEqual(CrfMetadata.objects.filter(visit_code="2000").count(), 1)
        self.assertEqual(RequisitionMetadata.objects.filter(visit_code="2000").count(), 0)

    def test_deletes_metadata_on_changed_reason(self):
        obj = SubjectVisit.objects.create(appointment=self.appointment, reason=SCHEDULED)
        self.assertGreater(CrfMetadata.objects.all().count(), 0)
        self.assertGreater(RequisitionMetadata.objects.all().count(), 0)
        obj.reason = MISSED_VISIT
        obj.save()
        self.assertEqual(CrfMetadata.objects.all().count(), 0)
        self.assertEqual(RequisitionMetadata.objects.all().count(), 0)

    def test_deletes_metadata_on_changed_reason_adds_back_crfs_missed(self):
        SubjectVisit.objects.create(appointment=self.appointment, reason=SCHEDULED)
        appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code="2000",
        )
        obj = SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)
        self.assertGreater(CrfMetadata.objects.all().count(), 0)
        self.assertGreater(RequisitionMetadata.objects.all().count(), 0)
        obj.reason = MISSED_VISIT
        obj.save()
        self.assertEqual(CrfMetadata.objects.filter(visit_code="2000").count(), 1)
        self.assertEqual(RequisitionMetadata.objects.filter(visit_code="2000").count(), 0)

    def test_deletes_metadata_on_delete_visit(self):
        obj = SubjectVisit.objects.create(appointment=self.appointment, reason=SCHEDULED)
        self.assertGreater(CrfMetadata.objects.all().count(), 0)
        self.assertGreater(RequisitionMetadata.objects.all().count(), 0)
        obj.delete()
        self.assertEqual(CrfMetadata.objects.all().count(), 0)
        self.assertEqual(RequisitionMetadata.objects.all().count(), 0)

    def test_deletes_metadata_on_delete_visit_even_for_missed(self):
        SubjectVisit.objects.create(appointment=self.appointment, reason=SCHEDULED)
        appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code="2000",
        )
        obj = SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)
        obj.reason = MISSED_VISIT
        obj.save()
        obj.delete()
        self.assertEqual(CrfMetadata.objects.filter(visit_code="2000").count(), 0)
        self.assertEqual(RequisitionMetadata.objects.filter(visit_code="2000").count(), 0)

    def test_raises_metadata_on_delete_visit_for_keyed_crf(self):
        obj = SubjectVisit.objects.create(appointment=self.appointment, reason=SCHEDULED)
        self.assertGreater(CrfMetadata.objects.all().count(), 0)
        CrfMetadata.objects.all().update(entry_status=KEYED)
        self.assertRaises(DeleteMetadataError, obj.delete)

    def test_raises_metadata_on_delete_visit_for_keyed_requisition(self):
        obj = SubjectVisit.objects.create(appointment=self.appointment, reason=SCHEDULED)
        self.assertGreater(RequisitionMetadata.objects.all().count(), 0)
        RequisitionMetadata.objects.all().update(entry_status=KEYED)
        self.assertRaises(DeleteMetadataError, obj.delete)
