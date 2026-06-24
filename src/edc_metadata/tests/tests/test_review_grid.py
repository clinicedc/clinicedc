from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.visit_schedules.visit_schedule_metadata.visit_schedule import (
    get_visit_schedule,
)
from django.contrib.auth.models import User
from django.test import TestCase, override_settings, tag
from django.test.client import RequestFactory

from edc_consent import site_consents
from edc_facility.import_holidays import import_holidays
from edc_lab.models.panel import Panel
from edc_metadata.constants import KEYED, REQUIRED
from edc_metadata.models import CrfMetadata, RequisitionMetadata
from edc_metadata.views.review_outstanding_grid_view import (
    ReviewOutstandingGridView,
    visit_columns,
)
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

utc_tz = ZoneInfo("UTC")


@tag("metadata")
@override_settings(SITE_ID=10)
@time_machine.travel(datetime(2019, 8, 11, 8, 00, tzinfo=utc_tz))
class TestReviewGrid(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        self.user = User.objects.create(username="erik")
        for name in ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]:
            Panel.objects.create(name=name)
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        visit_schedule = get_visit_schedule(consent_v1)
        site_visit_schedules.register(visit_schedule)

        helper = Helper()
        self.subject_visit = helper.enroll_to_baseline(
            visit_schedule_name=visit_schedule.name, schedule_name="schedule"
        )
        self.appointment = self.subject_visit.appointment
        self.subject_identifier = self.subject_visit.subject_identifier
        self.vsn = self.appointment.visit_schedule_name
        self.sn = self.appointment.schedule_name
        self.baseline = self.appointment.visit_code

    def base(self, **extra):
        opts = ReviewOutstandingGridView.base_filter(
            [10], self.vsn, self.sn, extra.pop("visit_code", None), extra.pop("q", None)
        )
        opts.update(extra)
        return opts

    # -------------------------------------------------------------- base_filter
    def test_base_filter_minimal(self):
        opts = ReviewOutstandingGridView.base_filter([10], self.vsn, self.sn, None, None)
        self.assertEqual(
            opts,
            dict(
                entry_status=REQUIRED,
                site_id__in=[10],
                visit_schedule_name=self.vsn,
                schedule_name=self.sn,
            ),
        )

    def test_base_filter_with_visit_and_subject(self):
        opts = ReviewOutstandingGridView.base_filter(
            [10], self.vsn, self.sn, self.baseline, "105"
        )
        self.assertEqual(opts["visit_code"], self.baseline)
        self.assertEqual(opts["subject_identifier__icontains"], "105")

    # ----------------------------------------------------------- count helpers
    def test_subject_totals_count_required_only(self):
        expected = CrfMetadata.objects.filter(
            entry_status=REQUIRED, site_id=10, subject_identifier=self.subject_identifier
        ).count()
        self.assertGreater(expected, 0)
        totals = ReviewOutstandingGridView._subject_totals(CrfMetadata, self.base())
        self.assertEqual(totals[self.subject_identifier], expected)

    def test_keyed_metadata_excluded_from_required_count(self):
        # The aggregation counts REQUIRED only. Flip one record to KEYED
        # directly (a plain save bypasses metadata rules) and confirm the
        # count drops by exactly one.
        sid = self.subject_identifier
        base = self.base()
        before = ReviewOutstandingGridView._subject_totals(CrfMetadata, base)[sid]
        pk = (
            CrfMetadata.objects.filter(
                entry_status=REQUIRED, site_id=10, subject_identifier=sid
            )
            .values_list("pk", flat=True)
            .first()
        )
        CrfMetadata.objects.filter(pk=pk).update(entry_status=KEYED)
        after = ReviewOutstandingGridView._subject_totals(CrfMetadata, base)[sid]
        self.assertEqual(after, before - 1)

    def test_cell_counts_keyed_by_subject_and_visit(self):
        expected = CrfMetadata.objects.filter(
            entry_status=REQUIRED,
            site_id=10,
            subject_identifier=self.subject_identifier,
            visit_code=self.baseline,
        ).count()
        cells = ReviewOutstandingGridView._cell_counts(
            CrfMetadata, self.base(), [self.subject_identifier]
        )
        self.assertEqual(cells[(self.subject_identifier, self.baseline)], expected)

    def test_model_filter_narrows_count(self):
        one = CrfMetadata.objects.filter(
            entry_status=REQUIRED, subject_identifier=self.subject_identifier
        ).values_list("model", flat=True)[0]
        totals = ReviewOutstandingGridView._subject_totals(
            CrfMetadata, self.base(model__in=[one])
        )
        self.assertEqual(totals[self.subject_identifier], 1)

    # ------------------------------------------------------------------- grid()
    def _grid(self, crf_only):
        view = ReviewOutstandingGridView()
        view.request = RequestFactory().get("/review/")
        view.request.user = self.user
        columns = visit_columns(self.vsn, self.sn)
        return (
            view.grid(
                self.base(), self.base(), columns, self.vsn, self.sn, crf_only, set(), set()
            ),
            columns,
        )

    def test_grid_totals_include_requisitions(self):
        crf_n = CrfMetadata.objects.filter(entry_status=REQUIRED, site_id=10).count()
        req_n = RequisitionMetadata.objects.filter(entry_status=REQUIRED, site_id=10).count()
        self.assertGreater(req_n, 0)
        ctx, _ = self._grid(crf_only=False)
        self.assertEqual(ctx["grand_total"], crf_n + req_n)
        self.assertEqual(ctx["subject_count"], 1)

    def test_grid_crf_only_excludes_requisitions(self):
        crf_n = CrfMetadata.objects.filter(entry_status=REQUIRED, site_id=10).count()
        ctx, _ = self._grid(crf_only=True)
        self.assertEqual(ctx["grand_total"], crf_n)

    def test_grid_cell_links_to_detail(self):
        ctx, columns = self._grid(crf_only=False)
        row = next(
            r for r in ctx["grid"] if r["subject_identifier"] == self.subject_identifier
        )
        baseline_index = [code for code, _ in columns].index(self.baseline)
        cell = row["cells"][baseline_index]
        self.assertIn("/detail/", cell["url"])
        self.assertIn(self.subject_identifier, cell["url"])
        self.assertGreater(cell["crf"], 0)
