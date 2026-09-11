from __future__ import annotations

from datetime import timedelta
from io import StringIO

import pandas as pd
from clinicedc_constants import FEMALE
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from django.core.management import color_style
from django.test import TestCase, override_settings, tag
from multisite import SiteID

from edc_consent import site_consents
from edc_lab_results_import.constants import MAX_DAYS_BEFORE_BASELINE
from edc_lab_results_import.result_importer.result_importer import ResultImporter
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


def make_importer(max_days_before_baseline: int | None = None) -> ResultImporter:
    """Builds a `ResultImporter` without `__init__`, which wants a real
    PDF folder and laboratory mapping files. See
    `test_result_importer_roundtrip`.
    """
    importer = ResultImporter.__new__(ResultImporter)
    importer.stdout = StringIO()
    importer.style = color_style()
    importer.max_days_before_baseline = (
        MAX_DAYS_BEFORE_BASELINE
        if max_days_before_baseline is None
        else max_days_before_baseline
    )
    return importer


@tag("lab_results_import")
@override_settings(SITE_ID=SiteID(10))
class TestMatchBaselineVisits(TestCase):
    """The two passes before this one match the specimen datetime
    against the visit report datetime by exact equality. A specimen
    drawn at screening and reported at baseline can never satisfy that,
    since the two datetimes are days apart by definition.
    """

    def setUp(self):
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(get_visit_schedule(consent_v1))
        self.subject_visit = Helper().enroll_to_baseline(
            visit_schedule_name="visit_schedule", schedule_name="schedule", gender=FEMALE
        )
        self.subject_identifier = self.subject_visit.subject_identifier
        self.baseline_datetime = pd.Timestamp(self.subject_visit.report_datetime).tz_convert(
            "UTC"
        )

    def get_df_related_visits(self) -> pd.DataFrame:
        """The frame `resolve_related_visits` matches against."""
        return pd.DataFrame(
            [
                dict(
                    subject_visit=str(self.subject_visit.id),
                    subject_identifier=self.subject_identifier,
                    visit_code=self.subject_visit.visit_code,
                    visit_code_sequence=self.subject_visit.visit_code_sequence,
                    visit_datetime=self.baseline_datetime,
                    schedule_name="schedule",
                )
            ]
        ).astype({"subject_visit": "string", "subject_identifier": "string"})

    def get_remaining(self, specimen_collected_datetime, **kwargs) -> pd.DataFrame:
        """A row the exact-equality passes left unmatched."""
        row = dict(
            subject_identifier=self.subject_identifier,
            utestid="haemoglobin",
            specimen_collected_datetime=specimen_collected_datetime,
            subject_visit=pd.NA,
            visit_code=pd.NA,
            visit_code_sequence=pd.NA,
            visit_datetime=pd.NaT,
        )
        row.update(**kwargs)
        df = pd.DataFrame([row]).astype({"subject_identifier": "string"})
        df["specimen_collected_datetime"] = pd.to_datetime(
            df["specimen_collected_datetime"], utc=True
        )
        return df

    def match(self, specimen_collected_datetime, max_days=None, **kwargs):
        importer = make_importer(max_days)
        return importer.match_baseline_visits(
            self.get_remaining(specimen_collected_datetime, **kwargs),
            self.get_df_related_visits(),
        )

    def test_matches_a_specimen_drawn_days_before_baseline(self):
        matched, remaining = self.match(self.baseline_datetime - timedelta(days=3))
        self.assertEqual(1, len(matched))
        self.assertEqual(0, len(remaining))
        self.assertEqual(str(self.subject_visit.id), matched.iloc[0]["subject_visit_right"])

    def test_matches_a_specimen_drawn_at_baseline(self):
        matched, _ = self.match(self.baseline_datetime)
        self.assertEqual(1, len(matched))

    def test_matches_at_the_bound(self):
        matched, _ = self.match(
            self.baseline_datetime - timedelta(days=MAX_DAYS_BEFORE_BASELINE)
        )
        self.assertEqual(1, len(matched))

    def test_does_not_match_beyond_the_bound(self):
        """`before baseline` alone would claim a specimen drawn a year
        earlier.
        """
        matched, remaining = self.match(
            self.baseline_datetime - timedelta(days=MAX_DAYS_BEFORE_BASELINE + 1)
        )
        self.assertEqual(0, len(matched))
        self.assertEqual(1, len(remaining))

    def test_the_bound_is_configurable(self):
        drawn = self.baseline_datetime - timedelta(days=60)
        self.assertEqual(0, len(self.match(drawn)[0]))
        self.assertEqual(1, len(self.match(drawn, max_days=90)[0]))

    def test_does_not_match_a_specimen_drawn_after_baseline(self):
        """It could belong to any later timepoint, so baseline is not
        the only candidate.
        """
        matched, remaining = self.match(self.baseline_datetime + timedelta(days=1))
        self.assertEqual(0, len(matched))
        self.assertEqual(1, len(remaining))

    def test_does_not_match_where_the_specimen_has_no_datetime(self):
        matched, remaining = self.match(None)
        self.assertEqual(0, len(matched))
        self.assertEqual(1, len(remaining))

    def test_does_not_match_an_unknown_subject(self):
        """With no subject there is no baseline to compare against."""
        matched, remaining = self.match(
            self.baseline_datetime - timedelta(days=3), subject_identifier="999-99-9999-9"
        )
        self.assertEqual(0, len(matched))
        self.assertEqual(1, len(remaining))

    def test_remaining_keeps_the_original_columns(self):
        """`resolve_related_visits` feeds `remaining` back into a
        concat, so it must not grow the merge's columns.
        """
        remaining_in = self.get_remaining(self.baseline_datetime + timedelta(days=1))
        _, remaining_out = make_importer().match_baseline_visits(
            remaining_in, self.get_df_related_visits()
        )
        self.assertEqual(list(remaining_in.columns), list(remaining_out.columns))
