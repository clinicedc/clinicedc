from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from edc_constants.constants import NO, YES

from ..forms import SubjectLocatorFormValidator


class TestFormValidator(TestCase):

    def test_may_not_call(self):
        cleaned_data = {
            'may_call': NO,
            'subject_cell': 12345678,
            'subject_phone': 12345678}
        form_validator = SubjectLocatorFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('subject_cell', form_validator._errors)
        self.assertIn('subject_phone', form_validator._errors)

    def test_may_call_no_numbers(self):
        cleaned_data = {
            'may_call': YES,
            'subject_cell': None,
            'subject_phone': None}
        form_validator = SubjectLocatorFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('subject_cell', form_validator._errors)
        self.assertIn('subject_phone', form_validator._errors)
