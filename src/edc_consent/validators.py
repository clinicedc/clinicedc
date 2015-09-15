from datetime import date
from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.core.exceptions import ValidationError


class SubjectTypeValidator:

    def __init__(self, subject_types):
        self.subject_types = subject_types

    def call(self, value):
        if value not in self.subject_types:
            raise ValidationError(
                'Undefined subject type. Expected one of {} for model {}. Got {}.'.format(
                    self.subject_types, self.model_cls._meta.verbose_name, value))


def MinConsentAge(dob):
    rdelta = relativedelta(date.today(), dob)
    if rdelta.years < settings.MIN_AGE_OF_CONSENT:
        raise ValidationError(
            'Participant must be {0}yrs or older. Got {1} using DOB=\'{}\'.'.format(
                settings.MIN_AGE_OF_CONSENT, rdelta.years, dob))


def MaxConsentAge(dob):
    rdelta = relativedelta(date.today(), dob)
    if rdelta.years > settings.MAX_AGE_OF_CONSENT:
        raise ValidationError(
            'Participant must be younger than {0}yrs. Got {1} using DOB=\'{}\'.'.format(
                settings.MAX_AGE_OF_CONSENT, rdelta.years, dob))


def ConsentAgeValidator(dob):
    MinConsentAge(dob)
    MaxConsentAge(dob)


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
