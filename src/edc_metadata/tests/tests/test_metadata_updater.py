from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.models import (
    CrfFive,
    CrfFour,
    CrfSix,
    SubjectRequisition,
)
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, override_settings, tag

from edc_lab.models import Panel
from edc_lab_panel.panels import fbc_panel, lft_panel
from edc_metadata.constants import KEYED, NOT_REQUIRED, REQUIRED
from edc_metadata.metadata_handler import MetadataHandlerError
from edc_metadata.metadata_inspector import MetaDataInspector
from edc_metadata.metadata_updater import MetadataUpdater
from edc_metadata.models import CrfMetadata, RequisitionMetadata
from edc_visit_tracking.models import SubjectVisit

from .metadata_test_mixin import TestMetadataMixin

utc_tz = ZoneInfo("UTC")


@override_settings(SITE_ID=10)
@time_machine.travel(datetime(2019, 8, 11, 8, 00, tzinfo=utc_tz))
@tag("metadata")
class TestMetadataUpdater(TestMetadataMixin, TestCase):
    def test_updates_crf_metadata_as_keyed(self):
        CrfFour.objects.create(subject_visit=self.subject_visit)
        self.assertEqual(
            CrfMetadata.objects.filter(
                entry_status=KEYED,
                model="clinicedc_tests.crffour",
                visit_code=self.subject_visit.visit_code,
            ).count(),
            1,
        )
        self.assertEqual(
            CrfMetadata.objects.filter(
                entry_status=REQUIRED,
                model="clinicedc_tests.crffive",
                visit_code=self.subject_visit.visit_code,
            ).count(),
            1,
        )
        self.assertEqual(
            CrfMetadata.objects.filter(
                entry_status=REQUIRED,
                model="clinicedc_tests.crfsix",
                visit_code=self.subject_visit.visit_code,
            ).count(),
            1,
        )

    def test_updates_all_crf_metadata_as_keyed(self):
        subject_visit = SubjectVisit.objects.get(appointment=self.appointment)
        CrfFour.objects.create(subject_visit=subject_visit)
        CrfFive.objects.create(subject_visit=subject_visit)
        CrfSix.objects.create(subject_visit=subject_visit)
        for model_name in ["crffour", "crffive", "crfsix"]:
            self.assertEqual(
                CrfMetadata.objects.filter(
                    entry_status=KEYED,
                    model=f"clinicedc_tests.{model_name}",
                    visit_code=subject_visit.visit_code,
                ).count(),
                1,
            )

    def test_updates_requisition_metadata_as_keyed(self):
        subject_visit = SubjectVisit.objects.get(appointment=self.appointment)
        SubjectRequisition.objects.create(
            subject_visit=subject_visit,
            panel=Panel.objects.get(name=fbc_panel.name),
        )
        self.assertEqual(
            RequisitionMetadata.objects.filter(
                entry_status=KEYED,
                model="clinicedc_tests.subjectrequisition",
                panel_name=fbc_panel.name,
                visit_code=subject_visit.visit_code,
            ).count(),
            1,
        )
        self.assertEqual(
            RequisitionMetadata.objects.filter(
                entry_status=REQUIRED,
                model="clinicedc_tests.subjectrequisition",
                panel_name=lft_panel.name,
                visit_code=subject_visit.visit_code,
            ).count(),
            1,
        )

    def test_resets_crf_metadata_on_delete(self):
        subject_visit = SubjectVisit.objects.get(appointment=self.appointment)
        crf_four = CrfFour.objects.create(subject_visit=subject_visit)
        crf_four.delete()
        self.assertEqual(
            CrfMetadata.objects.filter(
                entry_status=REQUIRED,
                model="clinicedc_tests.crffour",
                visit_code=subject_visit.visit_code,
            ).count(),
            1,
        )
        self.assertEqual(
            CrfMetadata.objects.filter(
                entry_status=REQUIRED,
                model="clinicedc_tests.crffive",
                visit_code=subject_visit.visit_code,
            ).count(),
            1,
        )
        self.assertEqual(
            CrfMetadata.objects.filter(
                entry_status=REQUIRED,
                model="clinicedc_tests.crfsix",
                visit_code=subject_visit.visit_code,
            ).count(),
            1,
        )

    def test_resets_requisition_metadata_on_delete1(self):
        subject_visit = SubjectVisit.objects.get(appointment=self.appointment)
        obj = SubjectRequisition.objects.create(
            subject_visit=subject_visit,
            panel=Panel.objects.get(name=fbc_panel.name),
        )
        obj.delete()
        self.assertEqual(
            RequisitionMetadata.objects.filter(
                entry_status=REQUIRED,
                model="clinicedc_tests.subjectrequisition",
                panel_name=fbc_panel.name,
                visit_code=subject_visit.visit_code,
            ).count(),
            1,
        )
        self.assertEqual(
            RequisitionMetadata.objects.filter(
                entry_status=REQUIRED,
                model="clinicedc_tests.subjectrequisition",
                panel_name=lft_panel.name,
                visit_code=subject_visit.visit_code,
            ).count(),
            1,
        )

    def test_resets_requisition_metadata_on_delete2(self):
        subject_visit = SubjectVisit.objects.get(appointment=self.appointment)
        obj = SubjectRequisition.objects.create(
            subject_visit=subject_visit,
            panel=Panel.objects.get(name=lft_panel.name),
        )
        obj.delete()
        self.assertEqual(
            RequisitionMetadata.objects.filter(
                entry_status=REQUIRED,
                model="clinicedc_tests.subjectrequisition",
                panel_name=fbc_panel.name,
                visit_code=subject_visit.visit_code,
            ).count(),
            1,
        )
        self.assertEqual(
            RequisitionMetadata.objects.filter(
                entry_status=REQUIRED,
                model="clinicedc_tests.subjectrequisition",
                panel_name=lft_panel.name,
                visit_code=subject_visit.visit_code,
            ).count(),
            1,
        )

    def test_get_metadata_for_subject_visit(self):
        """Asserts can get metadata for a subject and visit code."""
        subject_visit = SubjectVisit.objects.get(appointment=self.appointment)
        self.assertEqual(len(subject_visit.visit.all_crfs), 13)
        self.assertEqual(len(subject_visit.visit.all_requisitions), 4)

        metadata_a = []
        for values in subject_visit.metadata.values():
            for obj in values:
                try:
                    metadata_a.append(f"{obj.model}.{obj.panel_name}")
                except AttributeError:
                    metadata_a.append(obj.model)
        metadata_a.sort()
        forms = (
            subject_visit.schedule.visits.get(subject_visit.visit_code).scheduled_forms.forms
            + subject_visit.schedule.visits.get(subject_visit.visit_code).prn_forms.forms
        )
        metadata_b = [f.full_name for f in forms]
        metadata_b = list(set(metadata_b))
        metadata_b.sort()
        self.assertEqual(metadata_a, metadata_b)

    def test_metadata_inspector(self):
        subject_visit = SubjectVisit.objects.get(appointment=self.appointment)
        inspector = MetaDataInspector(
            model_cls=CrfFour,
            visit_schedule_name=subject_visit.visit_schedule_name,
            schedule_name=subject_visit.schedule_name,
            visit_code=subject_visit.visit_code,
            timepoint=subject_visit.timepoint,
        )
        self.assertEqual(len(inspector.required), 1)
        self.assertEqual(len(inspector.keyed), 0)

        CrfFour.objects.create(subject_visit=subject_visit)

        inspector = MetaDataInspector(
            model_cls=CrfFour,
            visit_schedule_name=subject_visit.visit_schedule_name,
            schedule_name=subject_visit.schedule_name,
            visit_code=subject_visit.visit_code,
            timepoint=subject_visit.timepoint,
        )
        self.assertEqual(len(inspector.required), 0)
        self.assertEqual(len(inspector.keyed), 1)

    def test_crf_updates_ok(self):
        subject_visit = SubjectVisit.objects.get(appointment=self.appointment)
        CrfMetadata.objects.get(
            visit_code=subject_visit.visit_code,
            model="clinicedc_tests.crffour",
            entry_status=REQUIRED,
        )
        metadata_updater = MetadataUpdater(
            related_visit=subject_visit,
            source_model="clinicedc_tests.crffour",
        )
        metadata_updater.get_and_update(entry_status=NOT_REQUIRED)
        self.assertRaises(
            ObjectDoesNotExist,
            CrfMetadata.objects.get,
            visit_code=subject_visit.visit_code,
            model="clinicedc_tests.crffour",
            entry_status=REQUIRED,
        )

        for visit_obj in SubjectVisit.objects.all():
            if visit_obj == subject_visit:
                try:
                    CrfMetadata.objects.get(
                        visit_code=visit_obj.visit_code,
                        model="clinicedc_tests.crffour",
                        entry_status=NOT_REQUIRED,
                    )
                except ObjectDoesNotExist as e:
                    self.fail(e)
            else:
                self.assertRaises(
                    ObjectDoesNotExist,
                    CrfMetadata.objects.get,
                    visit_code=visit_obj.visit_code,
                    model="clinicedc_tests.crffour",
                    entry_status=NOT_REQUIRED,
                )

    def test_crf_invalid_model(self):
        subject_visit = SubjectVisit.objects.get(appointment=self.appointment)
        metadata_updater = MetadataUpdater(
            related_visit=subject_visit,
            source_model="clinicedc_tests.blah",
        )
        self.assertRaises(
            MetadataHandlerError,
            metadata_updater.get_and_update,
            entry_status=NOT_REQUIRED,
        )

    @tag("metadata8")
    def test_crf_model_not_scheduled(self):
        subject_visit = SubjectVisit.objects.get(appointment=self.appointment)
        metadata_updater = MetadataUpdater(
            related_visit=subject_visit,
            source_model="clinicedc_tests.resultcrf",
        )
        self.assertRaises(
            MetadataHandlerError,
            metadata_updater.get_and_update,
            entry_status=NOT_REQUIRED,
        )
