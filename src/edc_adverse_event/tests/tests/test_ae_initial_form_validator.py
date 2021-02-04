from django import forms
from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from edc_constants.constants import NO, NOT_APPLICABLE, OTHER, YES
from edc_form_validators import NOT_REQUIRED_ERROR
from edc_list_data.site_list_data import site_list_data
from edc_sites.tests import SiteTestCaseMixin

from edc_adverse_event.models import SaeReason

from ...form_validators import AeInitialFormValidator, AeTmgFormValidator


class TestAeInitialFormValidator(SiteTestCaseMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        site_list_data.autodiscover()
        super().setUpClass()

    def test_ae_cause_yes(self):
        options = {"ae_cause": YES, "ae_cause_other": None}
        form_validator = AeInitialFormValidator(cleaned_data=options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn("ae_cause_other", form_validator._errors)

    def test_ae_cause_no(self):
        cleaned_data = {"ae_cause": NO, "ae_cause_other": YES}
        form_validator = AeInitialFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError:
            pass
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
        cleaned_data = {"ae_classification": OTHER, "ae_classification_other": None}
        form_validator = AeTmgFormValidator(cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn("ae_classification_other", form_validator._errors)

        cleaned_data = {"ae_classification": OTHER, "ae_classification_other": None}
        form_validator = AeTmgFormValidator(cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn("ae_classification_other", form_validator._errors)
