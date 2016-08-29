from __future__ import print_function

from django.utils import timezone

from edc_constants.constants import (
    SCHEDULED, NOT_REQUIRED, REQUIRED, KEYED, NEW, DEAD, NO, YES,
    COMPLETED_PROTOCOL_VISIT, OFF_STUDY, ALIVE, ON_STUDY)
from edc_meta_data.models import CrfMetaData, CrfEntry
from edc_testing.models import TestVisit, TestOffStudy, TestDeathReport

from .base_test_case import BaseTestCase


class TestMetaDataMixin(BaseTestCase):

    def test_changes_to_an_unscheduled_visit(self):
        """Assert changing to unscheduled visit sets all forms to not required."""
        visit = TestVisit.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now(),
            reason=SCHEDULED)
        self.assertEqual(
            CrfMetaData.objects.filter(
                registered_subject=self.appointment.registered_subject,
                entry_status=REQUIRED).count(), 3)
        visit.change_to_unscheduled_visit(self.appointment)
        self.assertEqual(
            [obj.entry_status for obj in CrfMetaData.objects.filter(
                registered_subject=self.appointment.registered_subject)],
            [NOT_REQUIRED, NOT_REQUIRED, NOT_REQUIRED])

    def test_change_to_off_study(self):
        """Assert changing to death visit adds off study and sets all others to not required."""
        TestVisit.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now(),
            study_status=OFF_STUDY,
            reason=COMPLETED_PROTOCOL_VISIT,
            require_crfs=NO)
        self.assertEqual(
            CrfMetaData.objects.filter(
                registered_subject=self.appointment.registered_subject,
                entry_status=REQUIRED).count(), 1)
        self.assertEqual(
            [obj.entry_status for obj in CrfMetaData.objects.filter(
                registered_subject=self.appointment.registered_subject)],
            [REQUIRED, NOT_REQUIRED, NOT_REQUIRED, NOT_REQUIRED])

    def test_change_to_off_study_creates_entry(self):
        """Assert changing to off study creates an Entry for off study."""
        TestVisit.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now(),
            study_status=OFF_STUDY,
            reason=COMPLETED_PROTOCOL_VISIT)
        crf_entry = CrfEntry.objects.get(
            content_type_map__app_label='edc_testing',
            content_type_map__module_name='testoffstudy')
        self.assertEqual(
            CrfMetaData.objects.filter(crf_entry=crf_entry).count(), 1)

    def test_require_death_report(self):
        """Assert death adds offstudy and death and sets all others to not required."""
        TestVisit.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now(),
            survival_status=DEAD,
            study_status=OFF_STUDY,
            reason=COMPLETED_PROTOCOL_VISIT,
            require_crfs=NO)
        self.assertEqual(
            [obj.entry_status for obj in CrfMetaData.objects.filter(
                registered_subject=self.appointment.registered_subject)],
            [REQUIRED, REQUIRED, NOT_REQUIRED, NOT_REQUIRED, NOT_REQUIRED])

    def test_require_death_report_require_crfs(self):
        """Assert changing to death visit adds offstudy and death and sets all others to not required."""
        TestVisit.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now(),
            survival_status=DEAD,
            reason=SCHEDULED,
            require_crfs=True)
        self.assertEqual(
            [obj.entry_status for obj in CrfMetaData.objects.filter(
                registered_subject=self.appointment.registered_subject)],
            [REQUIRED, REQUIRED, REQUIRED, REQUIRED])

    def test_require_death_report_creates_entry(self):
        """Assert changing to off study creates an Entry for death report."""
        TestVisit.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now(),
            survival_status=DEAD,
            reason=SCHEDULED)
        crf_entry = CrfEntry.objects.get(
            content_type_map__app_label='edc_testing',
            content_type_map__module_name='testdeathreport')
        self.assertEqual(
            CrfMetaData.objects.filter(crf_entry=crf_entry).count(), 1)

    def test_undo_require_death_report(self):
        visit = TestVisit.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now(),
            survival_status=DEAD,
            reason=SCHEDULED)
        visit.survival_status = ALIVE
        visit.save()
        crf_entry = CrfEntry.objects.get(
            content_type_map__app_label='edc_testing',
            content_type_map__module_name='testdeathreport')
        self.assertEqual(
            CrfMetaData.objects.filter(crf_entry=crf_entry).count(), 0)

    def test_undo_require_offstudy_report(self):
        visit = TestVisit.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now(),
            study_status=OFF_STUDY,
            reason=SCHEDULED)
        crf_entry = CrfEntry.objects.get(
            content_type_map__app_label='edc_testing',
            content_type_map__module_name='testoffstudy')
        self.assertEqual(
            CrfMetaData.objects.filter(crf_entry=crf_entry).count(), 1)
        visit.study_status = ON_STUDY
        visit.save()
        self.assertEqual(
            CrfMetaData.objects.filter(crf_entry=crf_entry).count(), 0)

    def test_undo_offstudy_visit_keyed(self):
        """Assert cannot remove crf meta data for off study if already keyed."""
        visit = TestVisit.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now(),
            study_status=OFF_STUDY,
            reason=SCHEDULED)
        crf_entry = CrfEntry.objects.get(
            content_type_map__app_label='edc_testing',
            content_type_map__module_name='testoffstudy')
        self.assertEqual(
            CrfMetaData.objects.filter(crf_entry=crf_entry, entry_status=NEW).count(), 1)
        TestOffStudy.objects.create(
            test_visit_model=visit,
            report_datetime=visit.report_datetime,
            offstudy_date=visit.report_datetime.date(),
            reason=SCHEDULED)
        self.assertEqual(
            CrfMetaData.objects.filter(crf_entry=crf_entry, entry_status=KEYED).count(), 1)
        visit.study_status = ON_STUDY
        visit.save()
        self.assertEqual(
            CrfMetaData.objects.filter(crf_entry=crf_entry).count(), 1)

    def test_undo_death_visit_keyed(self):
        """Assert cannot remove crf meta data for death visit if already keyed."""
        visit = TestVisit.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now(),
            survival_status=DEAD,
            study_status=OFF_STUDY,
            reason=SCHEDULED)
        TestOffStudy.objects.create(
            test_visit_model=visit,
            offstudy_date=visit.report_datetime.date(),
            reason=SCHEDULED)
        TestDeathReport.objects.create(
            test_visit=visit, report_datetime=visit.report_datetime)
        visit.survival_status = ALIVE
        visit.save()
        crf_entry = CrfEntry.objects.get(
            content_type_map__app_label='edc_testing',
            content_type_map__module_name='testoffstudy')
        self.assertEqual(
            CrfMetaData.objects.filter(crf_entry=crf_entry).count(), 1)
        crf_entry = CrfEntry.objects.get(
            content_type_map__app_label='edc_testing',
            content_type_map__module_name='testdeathreport')
        self.assertEqual(
            CrfMetaData.objects.filter(crf_entry=crf_entry).count(), 1)

    def test_completed_protocol(self):
        """Assert that if reason is completed protocol and crfs are being submitted then offstudy and all
        other crf are required.."""
        TestVisit.objects.create(
            appointment=self.appointment,
            report_datetime=timezone.now(),
            study_status=OFF_STUDY,
            reason=COMPLETED_PROTOCOL_VISIT,
            require_crfs=YES)
        self.assertEqual(
            CrfMetaData.objects.filter(
                registered_subject=self.appointment.registered_subject,
                entry_status=REQUIRED).count(), 4)
        self.assertEqual(
            [obj.entry_status for obj in CrfMetaData.objects.filter(
                registered_subject=self.appointment.registered_subject)],
            [REQUIRED, REQUIRED, REQUIRED, REQUIRED])
