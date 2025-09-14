from __future__ import annotations

from typing import TYPE_CHECKING

from django.forms import ValidationError
from django.test import TestCase

if TYPE_CHECKING:
    from edc_form_validators.form_validator import FormValidator
    from edc_model.models import BaseUuidModel


class FormValidatorTestCaseMixin:
    form_validator_cls: type[FormValidator] = None
    form_validator_model_cls: type[BaseUuidModel] = None

    def validate_form_validator(
        self: FormValidatorTestCaseMixin,
        cleaned_data: dict,
        *,
        instance: BaseUuidModel | None = None,
        model_cls: type[BaseUuidModel] | None = None,
        form_validator_cls: type[FormValidator] | None = None,
    ) -> FormValidator:
        form_validator = (form_validator_cls or self.form_validator_cls)(
            cleaned_data=cleaned_data,
            model=model_cls or self.form_validator_model_cls,
            instance=instance,
        )
        try:
            form_validator.validate()
        except ValidationError:
            pass
        return form_validator

    def assertFormValidatorNoError(  # noqa
        self: FormValidatorTestCaseMixin | TestCase, form_validator
    ) -> None:
        self.assertDictEqual({}, form_validator._errors)

    def assertFormValidatorError(  # noqa
        self: FormValidatorTestCaseMixin | TestCase,
        field: str,
        expected_msg: str,
        form_validator,
        expected_errors: int | None = None,
    ) -> None:
        expected_errors = 1 if expected_errors is None else expected_errors
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
