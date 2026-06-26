from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings, tag

from edc_metadata.models import (
    CrfMetadataMissing,
    DataMissingReason,
    RequisitionMetadataMissing,
)


@tag("metadata")
@override_settings(SITE_ID=10)
class TestManageMissingModels(TestCase):
    def setUp(self):
        self.reason = DataMissingReason.objects.create(
            name="test_reason", display_name="Test reason"
        )

    def _crf_opts(self, **kw) -> dict:
        opts = dict(
            subject_identifier="105-0001",
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            visit_code="1000",
            visit_code_sequence=0,
            model="clinicedc_tests.crfone",
            reason=self.reason,
            site_id=10,
        )
        opts.update(kw)
        return opts

    def test_crf_natural_key_is_unique(self):
        CrfMetadataMissing.objects.create(**self._crf_opts())
        with transaction.atomic(), self.assertRaises(IntegrityError):
            CrfMetadataMissing.objects.create(**self._crf_opts())

    def test_requisition_panel_is_part_of_natural_key(self):
        base = dict(
            subject_identifier="105-0001",
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            visit_code="1000",
            visit_code_sequence=0,
            model="clinicedc_tests.subjectrequisition",
            reason=self.reason,
            site_id=10,
        )
        RequisitionMetadataMissing.objects.create(**base, panel_name="fbc")
        # a different panel for the same form is a distinct flag
        RequisitionMetadataMissing.objects.create(**base, panel_name="cd4")
        # the same panel collides
        with transaction.atomic(), self.assertRaises(IntegrityError):
            RequisitionMetadataMissing.objects.create(**base, panel_name="fbc")

    def test_history_retained_on_delete(self):
        history_cls = CrfMetadataMissing.history.model
        obj = CrfMetadataMissing.objects.create(**self._crf_opts())
        pk = obj.pk
        self.assertEqual(history_cls.objects.filter(id=pk).count(), 1)
        obj.delete()
        # the create (+) and delete (-) history rows survive the delete
        self.assertEqual(history_cls.objects.filter(id=pk).count(), 2)
        self.assertFalse(CrfMetadataMissing.objects.filter(id=pk).exists())
