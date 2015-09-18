import six
from django import get_version

from datetime import date
from dateutil.relativedelta import relativedelta

from django.core.exceptions import ValidationError


if get_version().startswith('1.6') and six.PY2:
    try:
        from edc.base.model.validators import (
            MinConsentAge as MinConsentAgeValidator,
            MaxConsentAge as MinConsentAgeValidator,
            datetime_not_future, datetime_not_before_study_start)
    except ImportError:
        from edc_base.model.validators import (
            MinConsentAgeValidator, MaxConsentAgeValidator,
            datetime_not_future, datetime_not_before_study_start)
else:
        from edc_base.model.validators import (
            MinConsentAgeValidator, MaxConsentAgeValidator,
            datetime_not_future, datetime_not_before_study_start)


class SubjectTypeValidator:

    def __init__(self, subject_types):
        self.subject_types = subject_types

    def call(self, value):
        if value not in self.subject_types:
            raise ValidationError(
                'Undefined subject type. Expected one of {} for model {}. Got {}.'.format(
                    self.subject_types, self.model_cls._meta.verbose_name, value))


class ConsentAgeValidator(object):

    def __init__(self, min_age_in_years, max_age_in_years):
        self.min_age = int(min_age_in_years)
        self.max_age = int(max_age_in_years)

    def __call__(self, dob):
        rdelta = relativedelta(date.today(), dob)
        if rdelta.years < self.min_age or rdelta.years > self.max_age:
            raise ValidationError(
                'Age of participant must be between {0} yrs and {1} yrs. '
                'Got {2} yrs using DoB of \'{3}\' relative to today.'.format(
                    self.min_age, self.max_age, rdelta.years, dob))


def dob_not_future(value):
    now = date.today()
    if now < value:
        raise ValidationError(u'Date of birth cannot be a future date. You entered {}.'.format(value))


def eligible_if_yes(value):
    if value != 'Yes':
        raise ValidationError('Participant is NOT ELIGIBLE. Registration cannot continue.')


def eligible_if_yes_or_declined(value):
    if value not in ['Yes', 'Declined']:
        raise ValidationError('Please provide the subject with a copy of the consent.')


def eligible_if_no(value):
    if value != 'No':
        raise ValidationError('Participant is NOT ELIGIBLE. Registration cannot continue.')


def eligible_if_unknown(value):
    if value != 'Unknown':
        raise ValidationError('Participant is NOT ELIGIBLE. Registration cannot continue.')


def eligible_if_female(value):
    if value != 'F':
        raise ValidationError('If gender not Female, Participant is NOT ELIGIBLE and registration cannot continue.')


def eligible_if_male(value):
    if value != 'M':
        raise ValidationError('If gender not Male, Participant is NOT ELIGIBLE and registration cannot continue.')


def eligible_if_negative(value):
    if value != 'NEG':
        raise ValidationError('Participant must be HIV Negative.'
                              'Participant is NOT ELIGIBLE and registration cannot continue.'
                              )


def eligible_if_positive(value):
    if value != 'POS':
        raise ValidationError('Participant must be HIV Positive.'
                              'Participant is NOT ELIGIBLE and registration cannot continue.'
                              )


def eligible_not_positive(value):
    if value == 'POS':
        raise ValidationError('Participant must be HIV Negative / Unknown.'
                              'Participant is NOT ELIGIBLE and registration cannot continue.'
                              )
