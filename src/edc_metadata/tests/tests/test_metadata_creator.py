from django.test import TestCase
from edc_appointment.models import Appointment
from edc_facility.import_holidays import import_holidays
from edc_visit_tracking.constants import MISSED_VISIT, SCHEDULED, UNSCHEDULED

from ...metadata import CreatesMetadataError
from ...metadata_updater import MetadataUpdater
from ...models import CrfMetadata, RequisitionMetadata
from ..models import SubjectVisit
from .metadata_test_mixin import TestMetadataMixin


class TestCreatesMetadata(TestMetadataMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super().setUpClass()

    def test_metadata_updater_repr(self):
        obj = MetadataUpdater()
        self.assertTrue(repr(obj))

    def test_creates_metadata_on_scheduled(self):
        SubjectVisit.objects.create(appointment=self.appointment, reason=SCHEDULED)
        self.assertGreater(CrfMetadata.objects.all().count(), 0)
        self.assertGreater(RequisitionMetadata.objects.all().count(), 0)

    def test_creates_metadata_on_unscheduled(self):
        SubjectVisit.objects.create(appointment=self.appointment, reason=UNSCHEDULED)
        self.assertGreater(CrfMetadata.objects.all().count(), 0)
        self.assertGreater(RequisitionMetadata.objects.all().count(), 0)

    def test_does_not_creates_metadata_on_missed_no_crfs_missed(self):
        SubjectVisit.objects.create(appointment=self.appointment, reason=MISSED_VISIT)
        self.assertEqual(CrfMetadata.objects.all().count(), 0)
        self.assertEqual(RequisitionMetadata.objects.all().count(), 0)

    def test_does_not_creates_metadata_on_missed_unless_crfs_missed(self):
        SubjectVisit.objects.create(appointment=self.appointment, reason=MISSED_VISIT)
        appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code="2000",
        )
        SubjectVisit.objects.create(appointment=appointment, reason=MISSED_VISIT)
        self.assertEqual(CrfMetadata.objects.all().count(), 1)
        self.assertEqual(RequisitionMetadata.objects.all().count(), 0)

    def test_unknown_reason_raises(self):
        self.assertRaises(
            CreatesMetadataError,
            SubjectVisit.objects.create,
            appointment=self.appointment,
            reason="ERIK",
        )

    def test_change_to_unknown_reason_raises(self):
        obj = SubjectVisit.objects.create(appointment=self.appointment, reason=SCHEDULED)
        obj.reason = "ERIK"
        self.assertRaises(CreatesMetadataError, obj.save)
