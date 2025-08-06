from datetime import date, datetime, timedelta

from django.core.exceptions import ValidationError
from edc_utils import get_utcnow


def datetime_not_future(utc_datetime: datetime) -> None:
    time_error = timedelta(minutes=10)
    if utc_datetime > get_utcnow() + time_error:
        raise ValidationError("Cannot be a future date/time")


def date_not_future(value: date) -> None:
    if value > get_utcnow().date():
        raise ValidationError("Cannot be a future date")


def date_is_past(value: date) -> None:
    if value > get_utcnow().date():
        raise ValidationError("Expected a past date")


def date_is_not_now(value: date) -> None:
    if value == get_utcnow().date():
        raise ValidationError("Cannot be today")


def datetime_is_future(utc_datetime: datetime) -> None:
    time_error = timedelta(minutes=10)
    if utc_datetime < get_utcnow() + time_error:
        raise ValidationError("Expected a future date/time")


def date_is_future(value: date) -> None:
    if value < get_utcnow().date():
        raise ValidationError("Expected a future date")
