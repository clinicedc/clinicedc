from django.test import TestCase, override_settings, tag

from edc_metadata.models import (
    CrfMetadataUnavailable,
    DataUnavailableReason,
    RequisitionMetadataUnavailable,
)
from edc_metadata.views.review_unavailable_view import ReviewOutstandingFlaggedView


@tag("metadata")
@override_settings(SITE_ID=10)
class TestReviewUnavailable(TestCase):
    def setUp(self):
        self.reason = DataUnavailableReason.objects.create(
            name="test_reason", display_name="Test reason"
        )
        common = dict(
            subject_identifier="105-0001",
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            visit_code="1000",
            visit_code_sequence=0,
            reason=self.reason,
            site_id=10,
        )
        CrfMetadataUnavailable.objects.create(model="clinicedc_tests.crfone", **common)
        RequisitionMetadataUnavailable.objects.create(
            model="clinicedc_tests.subjectrequisition", panel_name="fbc", **common
        )

    def test_gathers_rows_from_both_models(self):
        rows = ReviewOutstandingFlaggedView.gather_rows([10])
        self.assertEqual(len(rows), 2)
        forms = {r["form"] for r in rows}
        # requisition row carries its panel in the form label
        self.assertTrue(any("(fbc)" in f for f in forms))

    def test_site_scoped(self):
        self.assertEqual(ReviewOutstandingFlaggedView.gather_rows([9999]), [])
        self.assertEqual(len(ReviewOutstandingFlaggedView.gather_rows([10])), 2)
