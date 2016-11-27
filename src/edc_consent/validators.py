import re

from dateutil.relativedelta import relativedelta


from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.timezone import localtime

from edc_base.utils import get_utcnow
from edc_constants.constants import YES, NO, DECLINED, UNKNOWN, MALE, NEG, POS


@deconstructible
class SubjectTypeValidator:

    def __init__(self, subject_types):
        self.subject_types = subject_types

    def __call__(self, value):
        if value not in self.subject_types:
            raise ValidationError(
                'Undefined subject type. Expected one of \'{subject_types}\'. Got \'{value}\'.',
                params={'subject_types': '\' or \''.join(self.subject_types), 'value': value})

    def __eq__(self, other):
        return self.subject_types == other.subject_types


@deconstructible
class FullNameValidator:

    def __init__(self, regex=None):
        self.regex = regex or re.compile('^[A-Z]{1,50}\, [A-Z]{1,50}$')

    def __call__(self, value):
        if not re.match(self.regex, value):
            raise ValidationError(
                'Invalid format. Format is \'LASTNAME, FIRSTNAME\'. All uppercase separated by a comma')

    def __eq__(self, other):
        return self.regex == other.regex


@deconstructible
class AgeTodayValidator(object):

    def __init__(self, min_age_in_years, max_age_in_years):
        self.min_age = int(min_age_in_years)
        self.max_age = int(max_age_in_years)

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__, self.min_age, self.max_age)

    def __call__(self, dob):
        rdelta = relativedelta(localtime(get_utcnow().date()), dob)
        if rdelta.years < self.min_age or rdelta.years > self.max_age:
            raise ValidationError(
                'Subject age is %(age)s yrs. Age of participant must be between '
                '%(min_age)s yrs and %(max_age)s yrs. Got DoB \'%(dob)s\' relative to \'TODAY\'.',
                code='invalid',
                params={'min_age': self.min_age, 'max_age': self.max_age, 'age': rdelta.years, 'dob': dob}
            )

    def __eq__(self, other):
        return self.min_age_in_years == other.min_age_in_years and self.max_age_in_years == other.max_age_in_years


def dob_not_future(value):
    now = get_utcnow().date()
    if now < value:
        raise ValidationError(
            'Date of birth cannot be a future date. You entered {}.'.format(value))


def eligible_if_yes(value):
    if value != YES:
        raise ValidationError('Participant is NOT ELIGIBLE. Registration cannot continue.')


def eligible_if_yes_or_declined(value):
    if value not in [YES, DECLINED]:
        raise ValidationError('Please provide the subject with a copy of the consent.')


def eligible_if_no(value):
    if value != NO:
        raise ValidationError('Participant is NOT ELIGIBLE. Registration cannot continue.')


def eligible_if_unknown(value):
    if value != UNKNOWN:
        raise ValidationError('Participant is NOT ELIGIBLE. Registration cannot continue.')


def eligible_if_female(value):
    if value != 'F':
        raise ValidationError(
            'If gender not Female, Participant is NOT ELIGIBLE and registration cannot continue.')


def eligible_if_male(value):
    if value != MALE:
        raise ValidationError(
            'If gender not Male, Participant is NOT ELIGIBLE and registration cannot continue.')


def eligible_if_negative(value):
    if value != NEG:
        raise ValidationError('Participant must be HIV Negative.'
                              'Participant is NOT ELIGIBLE and registration cannot continue.'
                              )


def eligible_if_positive(value):
    if value != POS:
        raise ValidationError('Participant must be HIV Positive.'
                              'Participant is NOT ELIGIBLE and registration cannot continue.'
                              )


def eligible_not_positive(value):
    if value == POS:
        raise ValidationError('Participant must be HIV Negative / Unknown.'
                              'Participant is NOT ELIGIBLE and registration cannot continue.'
                              )

# def gender_of_consent(value):
#     gender_list = [s for s in app_config]
#     if value not in gender_list:
#         raise ValidationError(u'Gender of consent not in {}. You entered {}.'.format(gender_list, value))
