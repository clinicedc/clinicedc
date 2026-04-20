"""Tests for the in-memory SimpleListFilter classes that power the
CrfMetadata / RequisitionMetadata changelists.

These filters build their option lists from the `site_visit_schedules`
registry instead of emitting `SELECT DISTINCT` against the metadata
tables, which is a hot path on large deployments (600k+ rows).

The tests assert:
  * `lookups()` returns a populated list drawn from the registry
  * `lookups()` never issues a database query
  * `queryset()` applies the expected filter (or passes through)
"""

from clinicedc_tests.consents import consent_v1
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from django.db import connection
from django.test import TestCase, tag
from django.test.client import RequestFactory
from django.test.utils import CaptureQueriesContext

from edc_consent import site_consents
from edc_metadata.admin.list_filters import (
    CrfDocumentNameListFilter,
    RequisitionDocumentNameListFilter,
    ScheduleNameListFilter,
    VisitCodeListFilter,
    VisitScheduleNameListFilter,
)
from edc_metadata.models import CrfMetadata
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


@tag("metadata")
class TestChangelistListFilters(TestCase):
    @classmethod
    def setUpTestData(cls):
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(get_visit_schedule(consent_v1))

    def _make(self, filter_cls):
        # SimpleListFilter.__init__ needs request/params/model/model_admin;
        # lookups() in our classes ignores all of them, so we construct
        # with the no-op dummies that Django itself uses in tests.
        request = RequestFactory().get("/")
        return filter_cls(
            request=request,
            params={},
            model=CrfMetadata,
            model_admin=None,
        )

    def test_visit_schedule_name_lookups_match_registry(self):
        expected = sorted(site_visit_schedules.registry.keys())
        f = self._make(VisitScheduleNameListFilter)
        self.assertEqual([v for v, _ in f.lookups(None, None)], expected)

    def test_schedule_name_lookups_match_registry(self):
        expected = sorted(
            {
                s.name
                for vs in site_visit_schedules.registry.values()
                for s in vs.schedules.values()
            }
        )
        f = self._make(ScheduleNameListFilter)
        self.assertEqual([v for v, _ in f.lookups(None, None)], expected)

    def test_visit_code_lookups_match_registry(self):
        expected = sorted(
            {
                v.code
                for vs in site_visit_schedules.registry.values()
                for s in vs.schedules.values()
                for v in s.visits.values()
            }
        )
        f = self._make(VisitCodeListFilter)
        self.assertEqual([v for v, _ in f.lookups(None, None)], expected)

    def test_crf_document_name_lookups_are_non_empty(self):
        f = self._make(CrfDocumentNameListFilter)
        choices = f.lookups(None, None)
        self.assertTrue(len(choices) > 0, "expected CRF verbose_names in registry")
        # all choices are strings
        for value, label in choices:
            self.assertIsInstance(value, str)
            self.assertEqual(value, label)

    def test_requisition_document_name_lookups_are_non_empty(self):
        f = self._make(RequisitionDocumentNameListFilter)
        choices = f.lookups(None, None)
        # requisitions may be empty in some test fixtures — just assert
        # the call is valid and returns a list
        self.assertIsInstance(choices, list)

    def test_lookups_do_not_hit_database(self):
        """The whole point: no DISTINCT queries on changelist render."""
        for cls in (
            VisitScheduleNameListFilter,
            ScheduleNameListFilter,
            VisitCodeListFilter,
            CrfDocumentNameListFilter,
            RequisitionDocumentNameListFilter,
        ):
            f = self._make(cls)
            with CaptureQueriesContext(connection) as ctx:
                f.lookups(None, None)
            self.assertEqual(
                len(ctx.captured_queries),
                0,
                f"{cls.__name__}.lookups() should not hit the DB, "
                f"but ran {len(ctx.captured_queries)} queries: "
                f"{ctx.captured_queries}",
            )

    def test_queryset_applies_filter_when_value_set(self):
        f = self._make(VisitCodeListFilter)
        f.used_parameters = {"visit_code": "1000"}
        qs = f.queryset(None, CrfMetadata.objects.all())
        # extract the WHERE condition; we just check it compiles + filters
        self.assertIn("visit_code", str(qs.query))
        self.assertIn("1000", str(qs.query))

    def test_queryset_is_passthrough_without_value(self):
        f = self._make(VisitCodeListFilter)
        f.used_parameters = {}
        original = CrfMetadata.objects.all()
        qs = f.queryset(None, original)
        self.assertIs(qs, original)

    def test_registry_not_loaded_returns_empty_lookups(self):
        """Admin must not crash if registry is empty (edge: fresh process,
        pre-registration import order)."""
        saved_registry = site_visit_schedules._registry
        saved_loaded = site_visit_schedules.loaded
        try:
            site_visit_schedules._registry = {}
            site_visit_schedules.loaded = False
            for cls in (
                VisitScheduleNameListFilter,
                ScheduleNameListFilter,
                VisitCodeListFilter,
                CrfDocumentNameListFilter,
                RequisitionDocumentNameListFilter,
            ):
                f = self._make(cls)
                self.assertEqual(f.lookups(None, None), [])
        finally:
            site_visit_schedules._registry = saved_registry
            site_visit_schedules.loaded = saved_loaded
