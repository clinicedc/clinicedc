import re

from django.core.exceptions import ValidationError


def TelephoneNumber(value, pattern, word):
    str_value = "%s" % (value)
    p = re.compile(pattern)
    if not p.match(str_value):
        raise ValidationError(u'Invalid %s number. You entered %s.' % (word, str_value))


def BWCellNumber(value):
    TelephoneNumber(value, '^[7]{1}[12345678]{1}[0-9]{6}$', 'cell')


def BWTelephoneNumber(value):
    TelephoneNumber(value, '^[2-8]{1}[0-9]{6}$', 'telephone')
