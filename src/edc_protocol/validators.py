import pytz

from django.apps import apps as django_apps
from django.utils import timezone
from django.core.exceptions import ValidationError

app_config = django_apps.get_app_config('edc_protocol')
tz = pytz.timezone('UTC')


def date_not_before_study_start(value):
    if value:
        try:
            value.date()
            raise TypeError('Expected date but got a datetime. Got {}'.format(value.strftime('%Y-%m-%d %H:%M')))
        except AttributeError:
            pass
        study_open_date = timezone.localtime(app_config.study_open_datetime).date()
        if value < study_open_date:
            raise ValidationError(
                'Invalid date. Study opened on {}. Got {}. See edc_protocol.AppConfig'.format(
                    study_open_date, value))


def datetime_not_before_study_start(value_datetime):
    if value_datetime:
        try:
            value_datetime.date()
        except AttributeError:
            raise TypeError('Expected datetime but got a date. Got {}'.format(value_datetime.strftime('%Y-%m-%d')))
        if value_datetime < app_config.study_open_datetime:
            raise ValidationError(
                'Invalid date/time. Study opened on {}. Got {}.'.format(
                    timezone.localtime(app_config.study_open_datetime).strftime('%Y-%m-%d %H:%M'),
                    timezone.localtime(value_datetime).strftime('%Y-%m-%d %H:%M')))
