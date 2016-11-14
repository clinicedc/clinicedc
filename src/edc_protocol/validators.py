import pytz

from datetime import datetime

from django.apps import apps as django_apps
from django.conf import settings
from django.utils.timezone import make_naive, make_aware
from django.core.exceptions import ValidationError

app_config = django_apps.get_app_config('edc_protocol')
tz = pytz.timezone(settings.TIME_ZONE)


def my_make_naive(value, tz):
    try:
        value = make_naive(value, tz)
    except ValueError:
        pass
    return value


def my_make_aware(value, tz):
    try:
        value = make_aware(value, tz)
    except ValueError:
        pass
    return value


def date_not_before_study_start(value):
    value_datetime = my_make_aware(datetime(value.year, value.month, value.day, 0, 0), tz)
    if value_datetime < app_config.study_open_datetime:
        raise ValidationError(
            'Invalid date. Study opened on {}. Got {}. See edc_protocol.AppConfig'.format(
                app_config.study_open_datetime, value_datetime))


def datetime_not_before_study_start(value):
    value = my_make_aware(value, tz)
    if value < app_config.study_open_datetime:
        raise ValidationError(
            'Invalid date. Study opened on {}. Got {}.'.format(app_config.study_open_datetime, value))
