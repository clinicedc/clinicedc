from django.db.models import ProtectedError
from django.test import TestCase
from edc_appointment.constants import INCOMPLETE_APPT, MISSED_APPT
from edc_appointment.models import Appointment
from edc_lab.models import Panel
from edc_visit_tracking.constants import MISSED_VISIT, SCHEDULED

from ...constants import KEYED, REQUIRED
from ...models import CrfMetadata, RequisitionMetadata
from ..models import CrfOne, SubjectRequisition, SubjectVisit
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
            8,
        )
        appointment.appt_timing = MISSED_APPT
        appointment.save()
        obj.reason = MISSED_VISIT
        obj.save()
        self.assertEqual(CrfMetadata.objects.filter(visit_code="2000").count(), 1)
        self.assertEqual(RequisitionMetadata.objects.filter(visit_code="2000").count(), 0)

    def test_deletes_metadata_on_changed_reason(self):
        SubjectVisit.objects.create(appointment=self.appointment, reason=SCHEDULED)
        self.appointment.appt_status = INCOMPLETE_APPT
        self.appointment.save()

        appointment = self.appointment.next
        obj = SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)
        self.assertGreater(CrfMetadata.objects.all().count(), 0)
        self.assertGreater(RequisitionMetadata.objects.all().count(), 0)

        appointment.appt_timing = MISSED_APPT
        appointment.save()
        appointment.refresh_from_db()
        self.assertEqual(appointment.appt_timing, MISSED_APPT)

        obj.refresh_from_db()
        self.assertEqual(obj.reason, MISSED_VISIT)
        obj.save()
        self.assertEqual(
            CrfMetadata.objects.filter(
                entry_status=REQUIRED, visit_code=appointment.visit_code
            ).count(),
            1,
        )
        self.assertEqual(
            RequisitionMetadata.objects.filter(
                entry_status=REQUIRED, visit_code=appointment.visit_code
            ).count(),
            0,
        )

    def test_deletes_metadata_on_changed_reason_adds_back_crfs_missed(self):
        SubjectVisit.objects.create(appointment=self.appointment, reason=SCHEDULED)
        appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code="2000",
        )
        obj = SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)
        self.assertGreater(CrfMetadata.objects.all().count(), 0)
        self.assertGreater(RequisitionMetadata.objects.all().count(), 0)
        appointment.appt_timing = MISSED_APPT
        appointment.save()
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
        subject_visit = SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)
        appointment.appt_timing = MISSED_APPT
        appointment.save()
        subject_visit.reason = MISSED_VISIT
        subject_visit.save()
        subject_visit.delete()
        self.assertEqual(CrfMetadata.objects.filter(visit_code="2000").count(), 0)
        self.assertEqual(RequisitionMetadata.objects.filter(visit_code="2000").count(), 0)

    def test_delete_visit_for_keyed_crf(self):
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED
        )
        self.assertGreater(CrfMetadata.objects.all().count(), 0)
        # delete
        subject_visit.delete()
        self.assertEqual(CrfMetadata.objects.all().count(), 0)
        # recreate
        subject_visit.save()
        self.assertGreater(CrfMetadata.objects.all().count(), 0)
        crf_one = CrfOne(subject_visit=subject_visit)
        crf_one.save()
        self.assertRaises(ProtectedError, subject_visit.delete)
        crf_one.delete()
        # create error condition, keyed but no model instances
        CrfMetadata.objects.all().update(entry_status=KEYED)
        subject_visit.delete()
        self.assertEqual(CrfMetadata.objects.all().count(), 0)

    def test_delete_visit_for_keyed_requisition(self):
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED
        )
        self.assertGreater(RequisitionMetadata.objects.all().count(), 0)
        panel = Panel.objects.get(name=RequisitionMetadata.objects.all()[0].panel_name)
        subject_requisition = SubjectRequisition.objects.create(
            subject_visit=subject_visit, panel=panel
        )
        RequisitionMetadata.objects.all().update(entry_status=KEYED)
        self.assertRaises(ProtectedError, subject_visit.delete)
        subject_requisition.delete()
        # create error condition, keyed but no model instances
        RequisitionMetadata.objects.all().update(entry_status=KEYED)
        subject_visit.delete()
        self.assertEqual(RequisitionMetadata.objects.all().count(), 0)
