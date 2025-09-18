from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import SubjectRequisition
from clinicedc_tests.sites import all_sites
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings, tag
from django.utils import timezone

from edc_consent import site_consents
from edc_constants.constants import NO, NOT_APPLICABLE, OTHER, YES
from edc_form_validators import FormValidator
from edc_lab.form_validators.requisition_form_validator import (
    RequisitionFormValidatorMixin,
)
from edc_lab.forms import BoxForm, BoxTypeForm, ManifestForm
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


@tag("lab")
@override_settings(SITE_ID=10)
class TestForms(TestCase):
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
        visit_schedule = get_visit_schedule(consent_v1)
        site_visit_schedules.register(visit_schedule=visit_schedule)

    def setUp(self):
        self.helper = self.helper_cls()
        subject_consent = self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
        )
        self.subject_identifier = subject_consent.subject_identifier

    def test_box_form_specimen_types1(self):
        data = {"specimen_types": "12, 13"}
        form = BoxForm(data=data)
        form.is_valid()
        self.assertNotIn("specimen_types", list(form.errors.keys()))

    def test_box_form_specimen_types2(self):
        data = {"specimen_types": None}
        form = BoxForm(data=data)
        form.is_valid()
        self.assertIn("specimen_types", list(form.errors.keys()))

    def test_box_form_specimen_types3(self):
        data = {"specimen_types": "AA, BB"}
        form = BoxForm(data=data)
        form.is_valid()
        self.assertIn("specimen_types", list(form.errors.keys()))

    def test_box_form_specimen_types4(self):
        data = {"specimen_types": "12, 13, AA"}
        form = BoxForm(data=data)
        form.is_valid()
        self.assertIn("specimen_types", list(form.errors.keys()))

    def test_box_form_specimen_types5(self):
        data = {"specimen_types": "12, 13, 13"}
        form = BoxForm(data=data)
        form.is_valid()
        self.assertIn("specimen_types", list(form.errors.keys()))

    def test_box_type_form1(self):
        data = {"across": 5, "down": 6, "total": 30}
        form = BoxTypeForm(data=data)
        form.is_valid()
        self.assertNotIn("total", list(form.errors.keys()))

    def test_box_type_form2(self):
        data = {"across": 5, "down": 6, "total": 10}
        form = BoxTypeForm(data=data)
        form.is_valid()
        self.assertIn("total", list(form.errors.keys()))

    def test_manifest_form1(self):
        data = {"category": OTHER, "category_other": None}
        form = ManifestForm(data=data)
        form.is_valid()
        self.assertIn("category_other", list(form.errors.keys()))

    def test_manifest_form2(self):
        data = {"category": "blah", "category_other": None}
        form = ManifestForm(data=data)
        form.is_valid()
        self.assertNotIn("category_other", list(form.errors.keys()))

    def test_requisition_form_reason(self):
        class MyRequisitionFormValidator(RequisitionFormValidatorMixin, FormValidator):
            report_datetime_field_attr = "requisition_datetime"

            @property
            def report_datetime(self):
                return self.cleaned_data.get(self.report_datetime_field_attr)

        data = {"is_drawn": YES, "reason_not_drawn": NOT_APPLICABLE}
        form_validator = MyRequisitionFormValidator(
            cleaned_data=data, model=SubjectRequisition
        )
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertNotIn("reason_not_drawn", cm.exception.error_dict)

        data = {
            "is_drawn": NO,
            "reason_not_drawn": "collection_failed",
            "item_type": NOT_APPLICABLE,
        }
        form_validator = MyRequisitionFormValidator(
            cleaned_data=data, model=SubjectRequisition
        )
        try:
            form_validator.validate()
        except ValidationError:
            self.fail("ValidationError unexpectedly raised")

    def test_requisition_form_drawn_not_drawn(self):
        class MyRequisitionFormValidator(RequisitionFormValidatorMixin, FormValidator):
            report_datetime_field_attr = "requisition_datetime"

            @property
            def report_datetime(self):
                return self.cleaned_data.get(self.report_datetime_field_attr)

        data = {
            "is_drawn": YES,
            "drawn_datetime": None,
            "requisition_datetime": timezone.now(),
        }
        form_validator = MyRequisitionFormValidator(
            cleaned_data=data, model=SubjectRequisition
        )
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("drawn_datetime", cm.exception.error_dict)

        self.assertEqual(
            cm.exception.error_dict.get("drawn_datetime")[0].message,
            "This field is required.",
        )

        data = {"is_drawn": NO, "drawn_datetime": timezone.now()}
        form_validator = MyRequisitionFormValidator(
            cleaned_data=data, model=SubjectRequisition
        )
        with self.assertRaises(ValidationError) as cm:
            form_validator.validate()
        self.assertIn("drawn_datetime", cm.exception.error_dict)
        self.assertEqual(
            cm.exception.error_dict.get("drawn_datetime")[0].message,
            "This field is not required.",
        )

        data = {"is_drawn": NO, "drawn_datetime": None}
        form_validator = MyRequisitionFormValidator(
            cleaned_data=data, model=SubjectRequisition
        )
        try:
            form_validator.validate()
        except ValidationError:
            self.fail("ValidationError unexpectedly raised")
