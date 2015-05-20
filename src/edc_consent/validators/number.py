from django.core.exceptions import ValidationError


def MinDecimalValidator(value, min_value):
    if min_value > value:
        raise ValidationError(u'Ensure this value is greater than or equal to %s.' % value)


def MaxDecimalValidator(value, max_value):
    if max_value < value:
        raise ValidationError(u'Ensure this value is less than or equal to %s.' % value)
