from datetime import date
from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.core.exceptions import ValidationError


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
