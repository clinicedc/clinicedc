from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag
from edc_visit_tracking.constants import SCHEDULED

from ...constants import KEYED, NOT_REQUIRED, REQUIRED
from ...metadata_handler import MetadataHandlerError
from ...metadata_inspector import MetaDataInspector
from ...metadata_updater import MetadataUpdater
from ...models import CrfMetadata, RequisitionMetadata
from ..models import CrfOne, CrfThree, CrfTwo, SubjectRequisition, SubjectVisit
from .metadata_test_mixin import TestMetadataMixin


class TestMetadataUpdater(TestMetadataMixin, TestCase):
    def test_updates_crf_metadata_as_keyed(self):
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED
        )
        CrfOne.objects.create(subject_visit=subject_visit)
        self.assertEqual(
            CrfMetadata.objects.filter(
                entry_status=KEYED,
                model="edc_metadata.crfone",
                visit_code=subject_visit.visit_code,
            ).count(),
            1,
        )
        self.assertEqual(
            CrfMetadata.objects.filter(
                entry_status=REQUIRED,
                model="edc_metadata.crftwo",
                visit_code=subject_visit.visit_code,
            ).count(),
            1,
        )
        self.assertEqual(
            CrfMetadata.objects.filter(
                entry_status=REQUIRED,
                model="edc_metadata.crfthree",
                visit_code=subject_visit.visit_code,
            ).count(),
            1,
        )

    def test_updates_all_crf_metadata_as_keyed(self):
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED
        )
        CrfOne.objects.create(subject_visit=subject_visit)
        CrfTwo.objects.create(subject_visit=subject_visit)
        CrfThree.objects.create(subject_visit=subject_visit)
        for model_name in ["crfone", "crftwo", "crfthree"]:
            self.assertEqual(
                CrfMetadata.objects.filter(
                    entry_status=KEYED,
                    model=f"edc_metadata.{model_name}",
                    visit_code=subject_visit.visit_code,
                ).count(),
                1,
            )

    def test_updates_requisition_metadata_as_keyed(self):
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED
        )
        SubjectRequisition.objects.create(subject_visit=subject_visit, panel=self.panel_one)
        self.assertEqual(
            RequisitionMetadata.objects.filter(
                entry_status=KEYED,
                model="edc_metadata.subjectrequisition",
                panel_name=self.panel_one.name,
                visit_code=subject_visit.visit_code,
            ).count(),
            1,
        )
        self.assertEqual(
            RequisitionMetadata.objects.filter(
                entry_status=REQUIRED,
                model="edc_metadata.subjectrequisition",
                panel_name=self.panel_two.name,
                visit_code=subject_visit.visit_code,
            ).count(),
            1,
        )

    def test_resets_crf_metadata_on_delete(self):
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED
        )
        crf_one = CrfOne.objects.create(subject_visit=subject_visit)
        crf_one.delete()
        self.assertEqual(
            CrfMetadata.objects.filter(
                entry_status=REQUIRED,
                model="edc_metadata.crfone",
                visit_code=subject_visit.visit_code,
            ).count(),
            1,
        )
        self.assertEqual(
            CrfMetadata.objects.filter(
                entry_status=REQUIRED,
                model="edc_metadata.crftwo",
                visit_code=subject_visit.visit_code,
            ).count(),
            1,
        )
        self.assertEqual(
            CrfMetadata.objects.filter(
                entry_status=REQUIRED,
                model="edc_metadata.crfthree",
                visit_code=subject_visit.visit_code,
            ).count(),
            1,
        )

    def test_resets_requisition_metadata_on_delete1(self):
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED
        )
        obj = SubjectRequisition.objects.create(
            subject_visit=subject_visit, panel=self.panel_one
        )
        obj.delete()
        self.assertEqual(
            RequisitionMetadata.objects.filter(
                entry_status=REQUIRED,
                model="edc_metadata.subjectrequisition",
                panel_name=self.panel_one.name,
                visit_code=subject_visit.visit_code,
            ).count(),
            1,
        )
        self.assertEqual(
            RequisitionMetadata.objects.filter(
                entry_status=REQUIRED,
                model="edc_metadata.subjectrequisition",
                panel_name=self.panel_two.name,
                visit_code=subject_visit.visit_code,
            ).count(),
            1,
        )

    @tag("2")
    def test_resets_requisition_metadata_on_delete2(self):
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED
        )
        obj = SubjectRequisition.objects.create(
            subject_visit=subject_visit, panel=self.panel_two
        )
        obj.delete()
        self.assertEqual(
            RequisitionMetadata.objects.filter(
                entry_status=REQUIRED,
                model="edc_metadata.subjectrequisition",
                panel_name=self.panel_one.name,
                visit_code=subject_visit.visit_code,
            ).count(),
            1,
        )
        self.assertEqual(
            RequisitionMetadata.objects.filter(
                entry_status=REQUIRED,
                model="edc_metadata.subjectrequisition",
                panel_name=self.panel_two.name,
                visit_code=subject_visit.visit_code,
            ).count(),
            1,
        )

    def test_get_metadata_for_subject_visit(self):
        """Asserts can get metadata for a subject and visit code."""
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED
        )
        metadata_a = []
        for metadata in subject_visit.metadata.values():
            for md in metadata:
                try:
                    metadata_a.append(f"{md.model}.{md.panel_name}")
                except AttributeError:
                    metadata_a.append(md.model)
        metadata_a.sort()
        metadata_b = [
            crf.model
            for crf in subject_visit.schedule.visits.get(subject_visit.visit_code).crfs
        ]
        metadata_b.extend(
            [
                f"{requisition.model}.{requisition.name}"
                for requisition in subject_visit.schedule.visits.get(
                    subject_visit.visit_code
                ).requisitions
            ]
        )
        metadata_b.sort()
        self.assertEqual(metadata_a, metadata_b)

    def test_metadata_inspector(self):
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED
        )
        inspector = MetaDataInspector(
            model_cls=CrfOne,
            visit_schedule_name=subject_visit.visit_schedule_name,
            schedule_name=subject_visit.schedule_name,
            visit_code=subject_visit.visit_code,
            timepoint=subject_visit.timepoint,
        )
        self.assertEqual(len(inspector.required), 1)
        self.assertEqual(len(inspector.keyed), 0)

        CrfOne.objects.create(subject_visit=subject_visit)

        inspector = MetaDataInspector(
            model_cls=CrfOne,
            visit_schedule_name=subject_visit.visit_schedule_name,
            schedule_name=subject_visit.schedule_name,
            visit_code=subject_visit.visit_code,
            timepoint=subject_visit.timepoint,
        )
        self.assertEqual(len(inspector.required), 0)
        self.assertEqual(len(inspector.keyed), 1)

    def test_crf_updates_ok(self):
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED
        )
        CrfMetadata.objects.get(
            visit_code=subject_visit.visit_code,
            model="edc_metadata.crfone",
            entry_status=REQUIRED,
        )
        metadata_updater = MetadataUpdater(
            related_visit=subject_visit,
            target_model="edc_metadata.crfone",
        )
        metadata_updater.get_and_update(entry_status=NOT_REQUIRED)
        self.assertRaises(
            ObjectDoesNotExist,
            CrfMetadata.objects.get,
            visit_code=subject_visit.visit_code,
            model="edc_metadata.crfone",
            entry_status=REQUIRED,
        )

        for visit_obj in SubjectVisit.objects.all():
            if visit_obj == subject_visit:
                try:
                    CrfMetadata.objects.get(
                        visit_code=visit_obj.visit_code,
                        model="edc_metadata.crfone",
                        entry_status=NOT_REQUIRED,
                    )
                except ObjectDoesNotExist as e:
                    self.fail(e)
            else:
                self.assertRaises(
                    ObjectDoesNotExist,
                    CrfMetadata.objects.get,
                    visit_code=visit_obj.visit_code,
                    model="edc_metadata.crfone",
                    entry_status=NOT_REQUIRED,
                )

    def test_crf_invalid_model(self):
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED
        )
        metadata_updater = MetadataUpdater(
            related_visit=subject_visit,
            target_model="edc_metadata.blah",
        )
        self.assertRaises(
            MetadataHandlerError, metadata_updater.get_and_update, entry_status=NOT_REQUIRED
        )

    def test_crf_model_not_scheduled(self):
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment, reason=SCHEDULED
        )
        metadata_updater = MetadataUpdater(
            related_visit=subject_visit,
            target_model="edc_metadata.crfseven",
        )
        self.assertRaises(
            MetadataHandlerError,
            metadata_updater.get_and_update,
            entry_status=NOT_REQUIRED,
        )
