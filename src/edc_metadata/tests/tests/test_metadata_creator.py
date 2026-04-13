from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, override_settings, tag

from edc_appointment.constants import IN_PROGRESS_APPT, MISSED_APPT
from edc_appointment.creators import create_unscheduled_appointment
from edc_appointment.tests.utils import create_related_visit
from edc_metadata.metadata import CreatesMetadataError, CrfCreator
from edc_metadata.metadata_updater import MetadataUpdater
from edc_metadata.models import CrfMetadata, RequisitionMetadata
from edc_visit_tracking.constants import MISSED_VISIT, SCHEDULED, UNSCHEDULED
from edc_visit_tracking.models import SubjectVisit

from .metadata_test_mixin import TestMetadataMixin

utc_tz = ZoneInfo("UTC")


@tag("metadata")
@override_settings(SITE_ID=10)
@time_machine.travel(datetime(2025, 8, 11, 8, 00, tzinfo=utc_tz))
class TestCreatesMetadata(TestMetadataMixin, TestCase):
    def test_metadata_updater_repr(self):
        obj = MetadataUpdater(related_visit=None, source_model=None)
        self.assertTrue(repr(obj))

    def test_creates_metadata_on_scheduled(self):
        self.assertEqual(CrfMetadata.objects.all().count(), 9)
        self.assertEqual(RequisitionMetadata.objects.all().count(), 4)

    def test_creates_metadata_on_unscheduled(self):
        appointment = create_unscheduled_appointment(
            appointment=self.appointment,
            next_appt_datetime=self.appointment.appt_datetime + relativedelta(days=1),
        )
        create_related_visit(appointment=appointment, reason=UNSCHEDULED)
        self.assertGreater(CrfMetadata.objects.all().count(), 9)
        self.assertEqual(RequisitionMetadata.objects.all().count(), 4)

    def test_does_not_creates_metadata_on_missed_no_crfs_missed(self):
        self.appointment_2000.appt_timing = MISSED_APPT
        self.appointment_2000.save()
        create_related_visit(self.appointment_2000, reason=MISSED_VISIT)

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
        subject_visit = SubjectVisit.objects.get(appointment=self.appointment)
        subject_visit.reason = "ERIK"
        self.assertRaises(
            CreatesMetadataError,
            subject_visit.save,
        )

    def test_change_to_unknown_reason_raises(self):
        obj = SubjectVisit.objects.get(appointment=self.appointment, reason=SCHEDULED)
        obj.reason = "ERIK"
        self.assertRaises(CreatesMetadataError, obj.save)

    @tag("metadata", "race_condition")
    def test_crf_creator_handles_integrity_error_on_race_condition(self):
        """Assert CrfCreator recovers when a concurrent request
        creates the metadata record between get() and create(),
        simulating a race condition.

        See also: IntegrityError on edc_metadata_crfmetadata_subject_iden_visit_uniq.
        """
        subject_visit = SubjectVisit.objects.get(appointment=self.appointment)
        # pick an existing metadata record
        existing = CrfMetadata.objects.filter(
            subject_identifier=subject_visit.subject_identifier,
            visit_code=self.appointment.visit_code,
        ).first()
        self.assertIsNotNone(existing)
        crf_model = existing.model

        # get the Crf definition from the visit schedule for this model
        crf = None
        for c in subject_visit.visit.crfs.forms:
            if c.model == crf_model:
                crf = c
                break
        self.assertIsNotNone(crf, f"Crf not found for {crf_model}")

        # Simulate the race condition: patch the queryset's get()
        # to raise ObjectDoesNotExist on the first call only (as if the
        # record doesn't exist yet), while the record actually exists in
        # the database. When create() is then called, it will hit the
        # unique constraint. The second get() call (the recovery path)
        # should succeed normally.
        original_get = CrfMetadata.objects.get
        call_count = 0

        def fake_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ObjectDoesNotExist()
            return original_get(**kwargs)

        creator = CrfCreator(
            crf=crf,
            update_keyed=True,
            related_visit=subject_visit,
        )

        with patch.object(type(CrfMetadata.objects), "get", side_effect=fake_get):
            # This should NOT raise CreatesMetadataError.
            # Instead it should recover and return the existing record.
            metadata_obj = creator.create()

        self.assertIsNotNone(metadata_obj)
        self.assertEqual(metadata_obj.model, crf_model)
