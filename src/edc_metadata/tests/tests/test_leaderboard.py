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
from edc_metadata.constants import REQUIRED
from edc_metadata.models import CrfMetadata
from edc_metadata.views.review_outstanding_grid_view import (
    ReviewOutstandingGridView,
    visit_columns,
)
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

utc_tz = ZoneInfo("UTC")


@tag("metadata")
@override_settings(SITE_ID=10)
@time_machine.travel(datetime(2019, 8, 11, 8, 00, tzinfo=utc_tz))
class TestLeaderboard(TestCase):
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

    def _view(self):
        view = ReviewOutstandingGridView()
        view.request = RequestFactory().get("/review/?site=")
        view.request.user = self.user
        return view

    def _leaderboard(self):
        view = self._view()
        return view.leaderboard(
            [10],
            self.vsn,
            self.sn,
            None,
            visit_columns(self.vsn, self.sn),
        )

    def test_one_row_per_required_crf_model_with_distinct_subjects(self):
        expected_models = set(
            CrfMetadata.objects.filter(
                entry_status=REQUIRED, site_id=10, visit_code=self.baseline
            ).values_list("model", flat=True)
        )
        rows = self._leaderboard()
        self.assertEqual({r["model"] for r in rows}, expected_models)
        for row in rows:
            # one enrolled subject -> distinct subject count of 1
            self.assertEqual(row["total"], 1)

    def test_cell_handoff_url_carries_model_and_visit(self):
        rows = self._leaderboard()
        row = rows[0]
        cell = next(c for c in row["cells"] if c["count"])
        self.assertIn("lens=grid", cell["url"])
        self.assertIn("visit_code=", cell["url"])
        self.assertIn("models=", cell["url"])

    def test_rows_sorted_by_descending_count(self):
        rows = self._leaderboard()
        totals = [r["total"] for r in rows]
        self.assertEqual(totals, sorted(totals, reverse=True))
