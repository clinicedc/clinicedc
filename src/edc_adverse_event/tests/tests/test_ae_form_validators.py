import contextlib

from clinicedc_constants import AE_WITHDRAWN, NO, NOT_APPLICABLE, OTHER, YES
from clinicedc_tests.action_items import register_actions
from clinicedc_tests.mixins import SiteTestCaseMixin
from clinicedc_tests.sites import all_sites
from django import forms
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings, tag

from edc_adverse_event.form_validators import (
    AeFollowupFormValidator,
    AeInitialFormValidator,
    AeTmgFormValidator,
)
from edc_adverse_event.models import AeClassification, SaeReason
from edc_facility.import_holidays import import_holidays
from edc_form_validators import NOT_REQUIRED_ERROR
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites


@tag("adverse_event")
@override_settings(EDC_LIST_DATA_ENABLE_AUTODISCOVER=False, SITE_ID=30)
class TestFormValidators(SiteTestCaseMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

    def setUp(self):
        register_actions()
        super().setUp()

    def test_ae_cause_yes(self):
        options = {"ae_cause": YES, "ae_cause_other": None}
        form_validator = AeInitialFormValidator(cleaned_data=options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn("ae_cause_other", form_validator._errors)

    def test_ae_cause_no(self):
        cleaned_data = {"ae_cause": NO, "ae_cause_other": YES}
        form_validator = AeInitialFormValidator(cleaned_data=cleaned_data)
        with contextlib.suppress(forms.ValidationError):
            form_validator.validate()
        self.assertIn("ae_cause_other", form_validator._errors)
        self.assertIn(NOT_REQUIRED_ERROR, form_validator._error_codes)

    def test_sae_reason_not_applicable(self):
        sae_reason = SaeReason.objects.get(name=NOT_APPLICABLE)
        cleaned_data = {"sae": YES, "sae_reason": sae_reason}
        form_validator = AeInitialFormValidator(cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn("sae_reason", form_validator._errors)

    def test_susar_reported_not_applicable(self):
        cleaned_data = {"susar": YES, "susar_reported": NOT_APPLICABLE}
        form_validator = AeInitialFormValidator(cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn("susar_reported", form_validator._errors)

    def test_ae_tmg_reported_ae_classification(self):
        ae_classification = AeClassification.objects.get(name=OTHER)
        cleaned_data = {
            "investigator_ae_classification": ae_classification,
            "investigator_ae_classification_other": None,
        }
        form_validator = AeTmgFormValidator(cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn("investigator_ae_classification_other", form_validator._errors)

        cleaned_data = {
            "investigator_ae_classification": ae_classification,
            "investigator_ae_classification_other": None,
        }
        form_validator = AeTmgFormValidator(cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn("investigator_ae_classification_other", form_validator._errors)

    def test_ae_followup(self):
        cleaned_data = {"outcome": None, "followup": None}
        form_validator = AeFollowupFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

        cleaned_data = {"outcome": AE_WITHDRAWN, "followup": None}
        form_validator = AeFollowupFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

        cleaned_data = {"outcome": AE_WITHDRAWN, "followup": NO}
        form_validator = AeFollowupFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError as e:
            self.fail(f"ValidationError unexpectedly raised. Got {e}")

        cleaned_data = {"outcome": AE_WITHDRAWN, "followup": YES}
        form_validator = AeFollowupFormValidator(cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn("followup", form_validator._errors)
