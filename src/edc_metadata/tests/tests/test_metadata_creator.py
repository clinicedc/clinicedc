from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.test import TestCase, override_settings, tag

from edc_appointment.constants import IN_PROGRESS_APPT, MISSED_APPT
from edc_appointment.creators import create_unscheduled_appointment
from edc_metadata.metadata import CreatesMetadataError
from edc_metadata.metadata_updater import MetadataUpdater
from edc_metadata.models import CrfMetadata, RequisitionMetadata
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit

from .metadata_test_mixin import TestMetadataMixin

utc_tz = ZoneInfo("UTC")


@tag("metadata")
@override_settings(SITE_ID=10)
@time_machine.travel(datetime(2025, 8, 11, 8, 00, tzinfo=utc_tz))
class TestCreatesMetadata(TestMetadataMixin, TestCase):
    def test_metadata_updater_repr(self):
        obj = MetadataUpdater()
        self.assertTrue(repr(obj))

    def test_creates_metadata_on_scheduled(self):
        self.assertGreater(CrfMetadata.objects.all().count(), 0)
        self.assertGreater(RequisitionMetadata.objects.all().count(), 0)

    def test_creates_metadata_on_unscheduled(self):
        create_unscheduled_appointment(
            next_appt_datetime=self.appointment.appt_datetime + relativedelta(days=1),
            appointment=self.appointment,
        )
        self.assertGreater(CrfMetadata.objects.all().count(), 0)
        self.assertGreater(RequisitionMetadata.objects.all().count(), 0)

    def test_does_not_creates_metadata_on_missed_no_crfs_missed(self):
        self.appointment_2000.appt_timing = MISSED_APPT
        self.appointment_2000.save_base(update_fields=["appt_timing"])
        self.assertEqual(
            CrfMetadata.objects.filter(visit_code=self.appointment_2000.visit_code).count(),
            1,
        )
        self.assertEqual(
            CrfMetadata.objects.filter(
                visit_code=self.appointment_2000.visit_code,
                model="edc_visit_tracking.subjectvisitmissed",
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
        subject_visit = SubjectVisit.objects.get(
            appointment=self.appointment,
            reason="ERIK",
        )
        subject_visit.reason = "ERIK"
        self.assertRaises(
            CreatesMetadataError,
            subject_visit.save,
        )

    def test_change_to_unknown_reason_raises(self):
        obj = SubjectVisit.objects.get(appointment=self.appointment, reason=SCHEDULED)
        obj.reason = "ERIK"
        self.assertRaises(CreatesMetadataError, obj.save)
