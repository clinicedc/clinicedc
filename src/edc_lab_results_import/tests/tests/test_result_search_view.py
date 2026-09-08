from __future__ import annotations

from decimal import Decimal
from importlib import import_module

from clinicedc_constants import (
    FEMALE,
    GRAMS_PER_DECILITER,
    GRAMS_PER_LITER,
    NO,
    YES,
)
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import BloodResultsFbc, SubjectRequisition
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.template.loader import get_template
from django.test import RequestFactory, TestCase, override_settings, tag
from django.urls import reverse
from django.utils import timezone

from edc_consent import site_consents
from edc_lab.models import Panel
from edc_lab_results_import.constants import DIFFERS, MATCH, NOT_COMPARED
from edc_lab_results_import.models import Result
from edc_lab_results_import.views import ResultSearchView
from edc_metadata.models import CrfMetadata
from edc_view_utils import ADD, CHANGE
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

User = get_user_model()


@tag("lab_results_import")
@override_settings(SITE_ID=10, ROOT_URLCONF="edc_lab_results_import.tests.urls")
class TestResultSearchViewButtons(TestCase):
    def setUp(self):
        # importing the app's urls registers `result_search_url` with
        # `url_names`. In a project this happens when the ROOT_URLCONF is
        # loaded, before any view runs.
        import_module("edc_lab_results_import.urls")
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(get_visit_schedule(consent_v1))

        self.subject_visit = Helper().enroll_to_baseline(
            visit_schedule_name="visit_schedule", schedule_name="schedule", gender=FEMALE
        )
        self.subject_identifier = self.subject_visit.subject_identifier
        self.requisition = SubjectRequisition.objects.create(
            subject_visit=self.subject_visit,
            panel=Panel.objects.get(name="fbc"),
            requisition_datetime=self.subject_visit.report_datetime,
        )
        self.user = User.objects.create(
            username="erik", is_superuser=True, is_active=True, is_staff=True
        )
        self.user.userprofile.sites.add(Site.objects.get(id=10))

    @property
    def view(self) -> ResultSearchView:
        return self.get_view()

    def get_view(self, url_kwargs: dict | None = None, **querystring) -> ResultSearchView:
        request = RequestFactory().get("/", querystring)
        request.user = self.user
        request.site = Site.objects.get(id=10)
        view = ResultSearchView()
        view.request = request
        view.kwargs = url_kwargs or {}
        return view

    def create_result(
        self,
        utestid: str,
        source_file: str | None = None,
        with_requisition: bool = True,
        result_value: Decimal | None = None,
        units: str | None = None,
        flag: str | None = None,
    ) -> Result:
        return Result.objects.create(
            subject_identifier=self.subject_identifier,
            screening_identifier="SCR0001",
            subject_visit=self.subject_visit,
            requisition=self.requisition if with_requisition else None,
            requisition_identifier=(
                self.requisition.requisition_identifier if with_requisition else ""
            ),
            visit_code=self.subject_visit.visit_code,
            visit_code_sequence=self.subject_visit.visit_code_sequence,
            panel_name="fbc",
            source_file=source_file or "report_001.pdf",
            utestid=utestid,
            source_utestid=utestid.upper(),
            result_value=result_value,
            units=units or "",
            flag=flag or "",
            result_no=f"RES-{utestid}",
            order_no="ORD001",
            sample_no="SAM001",
            result_status="final",
            name_id="NAME001",
            result_datetime=timezone.now(),
        )

    def test_rows_from_one_file_and_requisition_are_one_group(self):
        results = [self.create_result("haemoglobin"), self.create_result("wbc")]
        group_keys = {ResultSearchView.get_group_key(obj) for obj in results}
        self.assertEqual(1, len(group_keys))
        self.assertEqual(
            f"{self.requisition.id}|report_001.pdf",
            group_keys.pop(),
        )

    def test_second_source_file_is_a_second_group(self):
        results = [
            self.create_result("haemoglobin"),
            self.create_result("haemoglobin", source_file="report_002.pdf"),
        ]
        self.assertEqual(2, len({ResultSearchView.get_group_key(obj) for obj in results}))

    def test_one_add_button_for_one_result_set(self):
        results = [self.create_result("haemoglobin"), self.create_result("wbc")]
        buttons = self.view.get_crf_buttons(results)
        self.assertEqual(1, len(buttons))
        button = buttons[0]
        self.assertEqual(BloodResultsFbc, button.model_cls)
        self.assertEqual(ADD, button.action)
        self.assertEqual("", button.disabled)
        self.assertEqual(ResultSearchView.get_group_key(results[0]), button.group_key)

    def test_button_querystring_returns_to_search_and_fills_form(self):
        results = [self.create_result("haemoglobin")]
        querystring = self.view.get_crf_buttons(results)[0].querystring
        self.assertIn(
            "next=edc_lab_results_import:result_search_url,subject_identifier",
            querystring,
        )
        self.assertIn(f"subject_identifier={self.subject_identifier}", querystring)
        self.assertIn(f"subject_visit={self.subject_visit.id}", querystring)
        self.assertIn(f"requisition={self.requisition.id}", querystring)
        self.assertNotIn("appointment=", querystring)

    def test_button_is_a_change_button_once_the_crf_exists(self):
        BloodResultsFbc.objects.create(
            subject_visit=self.subject_visit, requisition=self.requisition
        )
        buttons = self.view.get_crf_buttons([self.create_result("haemoglobin")])
        self.assertEqual(CHANGE, buttons[0].action)

    def test_one_button_per_source_file(self):
        results = [
            self.create_result("haemoglobin"),
            self.create_result("haemoglobin", source_file="report_002.pdf"),
        ]
        self.assertEqual(2, len(self.view.get_crf_buttons(results)))

    def test_no_button_where_the_result_has_no_requisition(self):
        results = [self.create_result("haemoglobin", with_requisition=False)]
        self.assertEqual([], self.view.get_crf_buttons(results))

    def test_no_button_where_the_crf_has_no_metadata(self):
        CrfMetadata.objects.filter(
            subject_identifier=self.subject_identifier,
            model=BloodResultsFbc._meta.label_lower,
        ).delete()
        results = [self.create_result("haemoglobin")]
        self.assertEqual([], self.view.get_crf_buttons(results))

    def test_searches_on_requisition_identifier(self):
        result = self.create_result("haemoglobin")
        self.create_result("haemoglobin", source_file="other.pdf", with_requisition=False)
        view = self.get_view(requisition_identifier=self.requisition.requisition_identifier)
        self.assertEqual([result], view.get_results(view.get_search_terms()))

    def test_searches_on_a_partial_requisition_identifier(self):
        result = self.create_result("haemoglobin")
        requisition_identifier = self.requisition.requisition_identifier
        view = self.get_view(requisition_identifier=requisition_identifier[1:-1].lower())
        self.assertEqual([result], view.get_results(view.get_search_terms()))

    def test_search_terms_are_combined(self):
        self.create_result("haemoglobin")
        view = self.get_view(
            subject_identifier=self.subject_identifier,
            requisition_identifier="not-this-requisition",
        )
        self.assertEqual([], view.get_results(view.get_search_terms()))

    def test_no_search_term_returns_nothing(self):
        self.create_result("haemoglobin")
        view = self.get_view()
        self.assertEqual(
            {
                "subject_identifier": "",
                "screening_identifier": "",
                "requisition_identifier": "",
            },
            view.get_search_terms(),
        )
        self.assertEqual([], view.get_results(view.get_search_terms()))

    def test_subject_identifier_from_url_kwarg(self):
        result = self.create_result("haemoglobin")
        view = self.get_view(url_kwargs=dict(subject_identifier=self.subject_identifier))
        self.assertEqual(
            self.subject_identifier, view.get_search_terms()["subject_identifier"]
        )
        self.assertEqual([result], view.get_results(view.get_search_terms()))

    def test_requisition_identifier_search_is_carried_into_the_next_url(self):
        results = [self.create_result("haemoglobin")]
        requisition_identifier = self.requisition.requisition_identifier
        querystring = self.view.get_crf_buttons(
            results, requisition_identifier=requisition_identifier
        )[0].querystring
        self.assertIn(
            "next=edc_lab_results_import:result_search_url,subject_identifier,"
            "requisition_identifier",
            querystring,
        )
        self.assertIn(f"subject_identifier={self.subject_identifier}", querystring)
        self.assertIn(f"requisition_identifier={requisition_identifier}", querystring)

    def test_next_url_reverses_with_both_identifiers(self):
        requisition_identifier = self.requisition.requisition_identifier
        self.assertEqual(
            f"/edc_lab_results_import/result-search/{self.subject_identifier}/"
            f"{requisition_identifier}/",
            reverse(
                "edc_lab_results_import:result_search_url",
                kwargs=dict(
                    subject_identifier=self.subject_identifier,
                    requisition_identifier=requisition_identifier,
                ),
            ),
        )

    def test_search_form_is_filled_in_on_return_from_the_crf(self):
        result = self.create_result("haemoglobin")
        requisition_identifier = self.requisition.requisition_identifier
        view = self.get_view(
            url_kwargs=dict(
                subject_identifier=self.subject_identifier,
                requisition_identifier=requisition_identifier,
            )
        )
        search_terms = view.get_search_terms()
        self.assertEqual(
            {
                "subject_identifier": self.subject_identifier,
                "screening_identifier": "",
                "requisition_identifier": requisition_identifier,
            },
            search_terms,
        )
        self.assertEqual([result], view.get_results(search_terms))

    def test_no_comparison_until_the_crf_exists(self):
        results = [self.create_result("haemoglobin")]
        view = self.view
        self.assertEqual([], view.get_comparisons(results, view.get_crf_buttons(results)))

    def test_comparison_covers_only_utest_ids_on_the_crf(self):
        BloodResultsFbc.objects.create(
            subject_visit=self.subject_visit, requisition=self.requisition
        )
        results = [
            self.create_result("haemoglobin"),
            self.create_result("wbc"),
            # not a field on BloodResultsFbc
            self.create_result("creatinine"),
        ]
        view = self.view
        comparisons = view.get_comparisons(results, view.get_crf_buttons(results))
        self.assertEqual(1, len(comparisons))
        self.assertEqual(["haemoglobin", "wbc"], [row.utest_id for row in comparisons[0].rows])

    def test_comparison_matches_on_value_units_and_abnormal(self):
        BloodResultsFbc.objects.create(
            subject_visit=self.subject_visit,
            requisition=self.requisition,
            haemoglobin_value=Decimal("13.4"),
            haemoglobin_units=GRAMS_PER_DECILITER,
            haemoglobin_abnormal=NO,
        )
        results = [
            self.create_result(
                "haemoglobin", result_value=Decimal("13.4000"), units=GRAMS_PER_DECILITER
            )
        ]
        view = self.view
        row = view.get_comparisons(results, view.get_crf_buttons(results))[0].rows[0]
        self.assertFalse(row.differs)
        self.assertEqual(MATCH, row.value_status)
        self.assertEqual(MATCH, row.units_status)
        self.assertEqual(MATCH, row.abnormal_status)

    def test_comparison_flags_a_different_value(self):
        BloodResultsFbc.objects.create(
            subject_visit=self.subject_visit,
            requisition=self.requisition,
            haemoglobin_value=Decimal("13.5"),
            haemoglobin_units=GRAMS_PER_DECILITER,
        )
        results = [
            self.create_result(
                "haemoglobin", result_value=Decimal("13.4"), units=GRAMS_PER_DECILITER
            )
        ]
        view = self.view
        row = view.get_comparisons(results, view.get_crf_buttons(results))[0].rows[0]
        self.assertTrue(row.differs)
        self.assertEqual(DIFFERS, row.value_status)

    def test_comparison_does_not_compare_values_across_units(self):
        BloodResultsFbc.objects.create(
            subject_visit=self.subject_visit,
            requisition=self.requisition,
            haemoglobin_value=Decimal("13.4"),
            haemoglobin_units=GRAMS_PER_DECILITER,
        )
        results = [
            self.create_result("haemoglobin", result_value=Decimal(134), units=GRAMS_PER_LITER)
        ]
        view = self.view
        row = view.get_comparisons(results, view.get_crf_buttons(results))[0].rows[0]
        self.assertEqual(NOT_COMPARED, row.value_status)
        self.assertEqual(DIFFERS, row.units_status)
        self.assertTrue(row.differs)

    def test_comparison_uses_the_converted_value_where_it_matches_the_crf_units(self):
        BloodResultsFbc.objects.create(
            subject_visit=self.subject_visit,
            requisition=self.requisition,
            haemoglobin_value=Decimal("13.4"),
            haemoglobin_units=GRAMS_PER_DECILITER,
        )
        result = self.create_result(
            "haemoglobin", result_value=Decimal(134), units=GRAMS_PER_LITER
        )
        result.converted_result_value = Decimal("13.4")
        result.converted_units = GRAMS_PER_DECILITER
        result.save()
        view = self.view
        row = view.get_comparisons([result], view.get_crf_buttons([result]))[0].rows[0]
        self.assertEqual(MATCH, row.value_status)

    def test_comparison_flags_a_blank_crf_value(self):
        BloodResultsFbc.objects.create(
            subject_visit=self.subject_visit, requisition=self.requisition
        )
        results = [self.create_result("haemoglobin", result_value=Decimal("13.4"))]
        view = self.view
        row = view.get_comparisons(results, view.get_crf_buttons(results))[0].rows[0]
        self.assertEqual(DIFFERS, row.value_status)

    def test_comparison_maps_a_high_or_low_flag_to_abnormal(self):
        BloodResultsFbc.objects.create(
            subject_visit=self.subject_visit,
            requisition=self.requisition,
            haemoglobin_abnormal=NO,
        )
        results = [self.create_result("haemoglobin", flag="H")]
        view = self.view
        row = view.get_comparisons(results, view.get_crf_buttons(results))[0].rows[0]
        self.assertEqual(YES, row.abnormal)
        self.assertEqual(DIFFERS, row.abnormal_status)

    def test_comparison_does_not_interpret_an_unknown_flag(self):
        BloodResultsFbc.objects.create(
            subject_visit=self.subject_visit,
            requisition=self.requisition,
            haemoglobin_abnormal=NO,
        )
        results = [self.create_result("haemoglobin", flag="???")]
        view = self.view
        row = view.get_comparisons(results, view.get_crf_buttons(results))[0].rows[0]
        self.assertEqual(NOT_COMPARED, row.abnormal_status)

    def test_comparison_reads_a_blank_flag_as_not_abnormal(self):
        BloodResultsFbc.objects.create(
            subject_visit=self.subject_visit,
            requisition=self.requisition,
            haemoglobin_abnormal=NO,
        )
        results = [self.create_result("haemoglobin")]
        view = self.view
        row = view.get_comparisons(results, view.get_crf_buttons(results))[0].rows[0]
        self.assertEqual(NO, row.abnormal)
        self.assertEqual(MATCH, row.abnormal_status)

    def test_a_new_search_replaces_the_one_returned_to_from_the_crf(self):
        """The form submits a querystring while the url may still carry
        the kwargs of the search the CRF was opened from.
        """
        view = self.get_view(
            url_kwargs=dict(
                subject_identifier=self.subject_identifier,
                requisition_identifier=self.requisition.requisition_identifier,
            ),
            subject_identifier="999-99-9999-9",
            screening_identifier="",
            requisition_identifier="",
        )
        self.assertEqual(
            {
                "subject_identifier": "999-99-9999-9",
                "screening_identifier": "",
                "requisition_identifier": "",
            },
            view.get_search_terms(),
        )

    def test_a_search_on_one_field_clears_the_others(self):
        view = self.get_view(
            url_kwargs=dict(
                subject_identifier=self.subject_identifier,
                requisition_identifier=self.requisition.requisition_identifier,
            ),
            requisition_identifier="OTHER01",
        )
        self.assertEqual(
            {
                "subject_identifier": "",
                "screening_identifier": "",
                "requisition_identifier": "OTHER01",
            },
            view.get_search_terms(),
        )

    def test_template_compiles(self):
        self.assertTrue(get_template("edc_lab_results_import/result_search.html"))
