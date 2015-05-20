from django.core.exceptions import ValidationError

from ..choices import GENDER_OF_CONSENT


def GenderOfConsentValidator(value):
    gender_allowed = GENDER_OF_CONSENT
    if gender_allowed == 'MF':
        allowed = ('MF', 'Male and Female')
        entry = ('value', value)
    else:
        for lst in GENDER_OF_CONSENT:
            if lst[0] == gender_allowed:
                allowed = lst

        for lst in GENDER_OF_CONSENT:
            if lst[0] == value:
                entry = lst

    if value != allowed[0] and allowed[0] != 'MF':
        raise ValidationError(u'Gender of consent is %s. You entered %s.' % (allowed[1], entry[1]))
