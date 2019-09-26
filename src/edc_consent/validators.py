import re

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from edc_constants.constants import YES, NO, DECLINED, UNKNOWN, MALE, NEG, POS


@deconstructible
class SubjectTypeValidator:
    def __init__(self, subject_types):
        self.subject_types = subject_types

    def __call__(self, value):
        if value not in self.subject_types:
            raise ValidationError(
                "Undefined subject type. Expected one of '{subject_types}'. "
                "Got '{value}'.",
                params={
                    "subject_types": "' or '".join(self.subject_types),
                    "value": value,
                },
            )

    def __eq__(self, other):
        return self.subject_types == other.subject_types


@deconstructible
class FullNameValidator:
    def __init__(self, regex=None):
        self.regex = regex or re.compile("^[A-Z]{1,50}\, [A-Z]{1,50}$")

    def __call__(self, value):
        if not re.match(self.regex, value):
            raise ValidationError(
                "Invalid format. Format is 'LASTNAME, FIRSTNAME'. "
                "All uppercase separated by a comma. Note the space "
                "following the comma."
            )

    def __eq__(self, other):
        return self.regex == other.regex


def eligible_if_yes(value):
    if value != YES:
        raise ValidationError("Participant is not eligible.")


def eligible_if_yes_or_declined(value):
    if value not in [YES, DECLINED]:
        raise ValidationError("Please provide the subject with a copy of the consent.")


def eligible_if_no(value):
    if value != NO:
        raise ValidationError("Participant is not eligible.")


def eligible_if_unknown(value):
    if value != UNKNOWN:
        raise ValidationError("Participant is not eligible.")


def eligible_if_female(value):
    if value != "F":
        raise ValidationError("Expected 'Female', Participant is not eligible.")


def eligible_if_male(value):
    if value != MALE:
        raise ValidationError("Expected 'Male', Participant is not eligible.")


def eligible_if_negative(value):
    if value != NEG:
        raise ValidationError(
            "Participant must be HIV Negative." "Participant is not eligible."
        )


def eligible_if_positive(value):
    if value != POS:
        raise ValidationError(
            "Participant must be HIV Positive." "Participant is not eligible."
        )


def eligible_not_positive(value):
    if value == POS:
        raise ValidationError(
            "Participant must be HIV Negative / Unknown." "Participant is not eligible."
        )
