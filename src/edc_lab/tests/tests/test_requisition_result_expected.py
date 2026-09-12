from __future__ import annotations

from datetime import timedelta

from clinicedc_constants import NO, NOT_APPLICABLE, OTHER, YES
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import SubjectRequisition
from clinicedc_tests.sites import all_sites
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings, tag
from django.utils import timezone
from multisite import SiteID

from edc_consent import site_consents
from edc_form_validators import FormValidator
from edc_lab.form_validators.requisition_form_validator import (
    RequisitionFormValidatorMixin,
)
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


class MyRequisitionFormValidator(RequisitionFormValidatorMixin, FormValidator):
    report_datetime_field_attr = "requisition_datetime"

    @property
    def report_datetime(self):
        return self.cleaned_data.get(self.report_datetime_field_attr)


@tag("lab")
@override_settings(SITE_ID=SiteID(10))
class TestRequisitionResultExpected(TestCase):
    """A drawn specimen may still never yield a result. See
    `RESULT_NOT_EXPECTED_REASONS`.
    """

    helper_cls = Helper

    @classmethod
    def setUpTestData(cls):
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=get_visit_schedule(consent_v1))

    def setUp(self):
        self.helper = self.helper_cls()
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule", schedule_name="schedule"
        )
        self.now = timezone.now()

    def get_cleaned_data(self, **kwargs) -> dict:
        """Return cleaned data for a drawn specimen, valid up to the
        `result_expected` fields.
        """
        cleaned_data = dict(
            requisition_datetime=self.now,
            is_drawn=YES,
            reason_not_drawn=NOT_APPLICABLE,
            drawn_datetime=self.now,
            item_type="tube",
            item_count=1,
            estimated_volume=5,
            result_expected=YES,
            result_not_expected_reason=NOT_APPLICABLE,
            result_not_expected_reason_other="",
            result_not_expected_datetime=None,
        )
        cleaned_data.update(**kwargs)
        return cleaned_data

    def validate(self, **kwargs) -> None:
        MyRequisitionFormValidator(
            cleaned_data=self.get_cleaned_data(**kwargs), model=SubjectRequisition
        ).validate()

    def assert_invalid(self, field: str, **kwargs) -> ValidationError:
        with self.assertRaises(ValidationError) as cm:
            self.validate(**kwargs)
        self.assertIn(field, cm.exception.error_dict)
        return cm.exception

    def assert_valid(self, **kwargs) -> None:
        try:
            self.validate(**kwargs)
        except ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

    def test_a_drawn_specimen_expecting_a_result_is_valid(self):
        self.assert_valid()

    def test_result_expected_is_not_applicable_if_not_drawn(self):
        """Nothing was drawn, so there is nothing to expect a result
        from.
        """
        self.assert_invalid(
            "result_expected",
            is_drawn=NO,
            reason_not_drawn="collection_failed",
            drawn_datetime=None,
            item_type=NOT_APPLICABLE,
            item_count=None,
            estimated_volume=None,
            result_expected=YES,
        )

    def test_not_applicable_result_expected_is_valid_if_not_drawn(self):
        self.assert_valid(
            is_drawn=NO,
            reason_not_drawn="collection_failed",
            drawn_datetime=None,
            item_type=NOT_APPLICABLE,
            item_count=None,
            estimated_volume=None,
            result_expected=NOT_APPLICABLE,
        )

    def test_reason_is_required_if_no_result_is_expected(self):
        self.assert_invalid(
            "result_not_expected_reason",
            result_expected=NO,
            result_not_expected_reason=NOT_APPLICABLE,
            result_not_expected_datetime=self.now,
        )

    def test_reason_is_not_applicable_if_a_result_is_expected(self):
        self.assert_invalid(
            "result_not_expected_reason",
            result_expected=YES,
            result_not_expected_reason="30",
        )

    def test_a_reason_is_valid_if_no_result_is_expected(self):
        """30 is clotted or haemolised."""
        self.assert_valid(
            result_expected=NO,
            result_not_expected_reason="30",
            result_not_expected_datetime=self.now,
        )

    def test_other_reason_requires_the_other_field(self):
        self.assert_invalid(
            "result_not_expected_reason_other",
            result_expected=NO,
            result_not_expected_reason=OTHER,
            result_not_expected_reason_other="",
            result_not_expected_datetime=self.now,
        )

    def test_other_reason_with_the_other_field_is_valid(self):
        self.assert_valid(
            result_expected=NO,
            result_not_expected_reason=OTHER,
            result_not_expected_reason_other="Sample lost in transit",
            result_not_expected_datetime=self.now,
        )

    def test_datetime_is_required_if_no_result_is_expected(self):
        self.assert_invalid(
            "result_not_expected_datetime",
            result_expected=NO,
            result_not_expected_reason="30",
            result_not_expected_datetime=None,
        )

    def test_datetime_is_not_required_if_a_result_is_expected(self):
        self.assert_invalid(
            "result_not_expected_datetime",
            result_expected=YES,
            result_not_expected_reason=NOT_APPLICABLE,
            result_not_expected_datetime=self.now,
        )

    def test_datetime_may_not_precede_the_draw(self):
        """The site cannot have decided before the specimen existed."""
        exception = self.assert_invalid(
            "result_not_expected_datetime",
            result_expected=NO,
            result_not_expected_reason="30",
            drawn_datetime=self.now,
            result_not_expected_datetime=self.now - timedelta(days=1),
        )
        self.assertEqual(
            "May not be before date/time specimen drawn",
            exception.error_dict.get("result_not_expected_datetime")[0].message,
        )

    def test_datetime_after_the_draw_is_valid(self):
        self.assert_valid(
            result_expected=NO,
            result_not_expected_reason="30",
            drawn_datetime=self.now - timedelta(days=1),
            result_not_expected_datetime=self.now,
        )

    def test_datetime_equal_to_the_draw_is_valid(self):
        self.assert_valid(
            result_expected=NO,
            result_not_expected_reason="30",
            drawn_datetime=self.now,
            result_not_expected_datetime=self.now,
        )
