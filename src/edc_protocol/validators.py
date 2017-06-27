import arrow

from dateutil.tz import gettz

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


def date_not_before_study_start(value):
    if value:
        app_config = django_apps.get_app_config('edc_protocol')
        tzinfo = gettz(settings.TIME_ZONE)
        value_utc = arrow.Arrow.fromdate(value, tzinfo).to('utc').datetime
        if value_utc < app_config.study_open_datetime:
            raise ValidationError(
                'Invalid date. Study opened on {}. Got {}. '
                'See edc_protocol.AppConfig'.format(
                    timezone.localtime(
                        app_config.study_open_datetime).strftime('%Y-%m-%d'),
                    timezone.localtime(value_utc).strftime('%Y-%m-%d')))


def datetime_not_before_study_start(value_datetime):
    if value_datetime:
        app_config = django_apps.get_app_config('edc_protocol')
        value_utc = arrow.Arrow.fromdatetime(
            value_datetime, value_datetime.tzinfo).to('utc').datetime
        if value_utc < app_config.study_open_datetime:
            raise ValidationError(
                'Invalid date/time. Study opened on {}. Got {}.'.format(
                    timezone.localtime(app_config.study_open_datetime).strftime(
                        '%Y-%m-%d %H:%M'),
                    timezone.localtime(value_utc).strftime('%Y-%m-%d %H:%M')))
