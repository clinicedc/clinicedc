from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import SubjectRequisition
from clinicedc_tests.visit_schedules.visit_schedule_lab_results.lab_profiles import (
    lab_profile,
)
from clinicedc_tests.visit_schedules.visit_schedule_lab_results.visit_schedule import (
    get_visit_schedule,
)
from django.test import TestCase, override_settings, tag

from edc_action_item.site_action_items import site_action_items
from edc_consent import site_consents
from edc_lab import site_labs
from edc_lab.models import Panel
from edc_lab_results.action_items import register_actions
from edc_lab_results.constants import LINKED, NO_MATCH
from edc_lab_results.models import Result
from edc_lab_results.views import OrderDetailView
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

ORDER_NO = "ORD-1"


@tag("lab_results")
@override_settings(SITE_ID=10)
class TestLinkOrderToVisit(TestCase):
    """OrderDetailView.link_order_to_visit_requisitions links each result to
    the requisition at the chosen visit whose panel reports its utest_id."""

    def setUp(self):
        helper = Helper()
        site_labs._registry = {}
        site_labs.register(lab_profile=lab_profile)
        site_action_items.registry = {}
        register_actions()
        site_consents.registry = {}
        site_consents.register(consent_v1)

        visit_schedule = get_visit_schedule(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)

        self.subject_visit = helper.enroll_to_baseline(
            visit_schedule_name=visit_schedule.name, schedule_name="schedule"
        )
        self.subject_identifier = self.subject_visit.subject_identifier

    def _create_result(self, utest_id: str = "haemoglobin") -> Result:
        return Result.objects.create(
            order_no=ORDER_NO,
            subject_identifier=self.subject_identifier,
            utest_id=utest_id,
            requisition_match_category=NO_MATCH,
            subject_not_found=False,
        )

    def _create_requisition(self, panel_name: str = "fbc") -> SubjectRequisition:
        return SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=Panel.objects.get(name=panel_name),
            requisition_datetime=self.subject_visit.report_datetime,
        )

    def _link(self) -> int:
        return OrderDetailView.link_order_to_visit_requisitions(
            ORDER_NO,
            self.subject_identifier,
            self.subject_visit.visit_code,
            self.subject_visit.visit_code_sequence,
        )

    def test_links_result_to_matching_visit_requisition(self):
        requisition = self._create_requisition(panel_name="fbc")
        self._create_result(utest_id="haemoglobin")  # haemoglobin is on fbc

        self.assertEqual(self._link(), 1)

        result = Result.objects.get(order_no=ORDER_NO)
        self.assertEqual(
            result.requisition_identifier, requisition.requisition_identifier
        )
        self.assertEqual(result.requisition_match_category, LINKED)
        self.assertFalse(result.requisition_ambiguous)
        self.assertEqual(result.requisition_candidates, [])

    def test_no_link_when_requisition_missing(self):
        # subject/visit exist, but no requisition at that visit
        self._create_result(utest_id="haemoglobin")

        self.assertEqual(self._link(), 0)

        result = Result.objects.get(order_no=ORDER_NO)
        self.assertEqual(result.requisition_identifier, "")
        self.assertEqual(result.requisition_match_category, NO_MATCH)

    def test_no_link_when_requisition_panel_differs(self):
        # a requisition exists at the visit, but for a different panel that is
        # registered in this lab_profile (blood_glucose, not fbc)
        self._create_requisition(panel_name="blood_glucose")
        self._create_result(utest_id="haemoglobin")  # haemoglobin is only on fbc

        self.assertEqual(self._link(), 0)

        result = Result.objects.get(order_no=ORDER_NO)
        self.assertEqual(result.requisition_identifier, "")
        self.assertEqual(result.requisition_match_category, NO_MATCH)

    def test_no_link_when_utest_id_not_on_any_panel(self):
        self._create_requisition(panel_name="fbc")
        self._create_result(utest_id="mono%")  # not on any registered panel

        self.assertEqual(self._link(), 0)

        result = Result.objects.get(order_no=ORDER_NO)
        self.assertEqual(result.requisition_identifier, "")
