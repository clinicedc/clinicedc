from typing import Any

from django.forms import ValidationError


class FormValidatorTestCaseMixin:

    form_validator_default_form_cls = None

    def validate_form_validator(self, cleaned_data, form_cls=None, instance=None):
        form_cls = form_cls or self.form_validator_default_form_cls
        form_validator = form_cls(cleaned_data=cleaned_data, instance=instance)
        try:
            form_validator.validate()
        except ValidationError:
            pass
        return form_validator

    def assertFormValidatorNoError(self: Any, form_validator):  # noqa
        self.assertDictEqual({}, form_validator._errors)

    def assertFormValidatorError(  # noqa
        self: Any,
        field: str,
        expected_msg: str,
        form_validator,
        expected_errors: int = 1,
    ):
        self.assertIn(
            field,
            form_validator._errors,
            msg=(
                f"Expected field '{field}' in form validation errors. "
                f"Got '{form_validator._errors}'."
            ),
        )
        self.assertIn(
            expected_msg,
            str(form_validator._errors.get(field)),
            msg=(
                f"Expected error message '{expected_msg}' for field '{field}' "
                f"in form validation errors.  Got '{form_validator._errors}'"
            ),
        )
        self.assertEqual(
            len(form_validator._errors),
            expected_errors,
            msg=(
                f"Expected {expected_errors} error message(s) in form validator. "
                f"Got {len(form_validator._errors)} errors "
                f"as follows: '{form_validator._errors}'"
            ),
        )
