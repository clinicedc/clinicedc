from datetime import datetime
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta
from django.test import TestCase, override_settings
from edc_appointment.constants import IN_PROGRESS_APPT, MISSED_APPT
from edc_visit_tracking.constants import SCHEDULED, UNSCHEDULED

from edc_metadata.metadata import CreatesMetadataError
from edc_metadata.metadata_updater import MetadataUpdater
from edc_metadata.models import CrfMetadata, RequisitionMetadata

from ..models import SubjectVisit
from .metadata_test_mixin import TestMetadataMixin

test_datetime = datetime(2019, 6, 11, 8, 00, tzinfo=ZoneInfo("UTC"))


@override_settings(
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=test_datetime - relativedelta(years=3),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=test_datetime + relativedelta(years=3),
)
class TestCreatesMetadata(TestMetadataMixin, TestCase):
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
        SubjectVisit.objects.create(appointment=self.appointment, reason=SCHEDULED)
        self.appointment_2000.appt_timing = MISSED_APPT
        self.appointment_2000.save_base(update_fields=["appt_timing"])
        self.assertEqual(
            CrfMetadata.objects.filter(visit_code=self.appointment_2000.visit_code).count(), 1
        )
        self.assertEqual(
            CrfMetadata.objects.filter(
                visit_code=self.appointment_2000.visit_code,
                model="edc_metadata.subjectvisitmissed",
            ).count(),
            1,
        )
        self.assertEqual(
            RequisitionMetadata.objects.filter(
                visit_code=self.appointment_2000.visit_code
            ).count(),
            0,
        )

    def test_unknown_reason_raises(self):
        self.appointment.appt_status = IN_PROGRESS_APPT
        self.appointment.save()
        self.appointment.refresh_from_db()
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
